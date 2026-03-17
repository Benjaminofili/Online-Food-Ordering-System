import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ArrowRight, Clock, Star, MapPin } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

export default function App() {
  const mainRef = useRef(null);
  const heroTextRef = useRef(null);
  const philosophyTextRef = useRef(null);
  const protocolCardsRef = useRef([]);

  // --- Audience State ---
  const [audience, setAudience] = useState('customer'); // 'customer' | 'restaurant'

  // We add a transition trigger when audience changes, gently fading the text
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (heroTextRef.current) {
        gsap.fromTo(heroTextRef.current, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.8, ease: "power2.out" });
    }
  }, [audience]);
  const initialRestaurants = [
    { name: "Le Petit Maison", tags: "French • 4.9 ★", style: "z-30 translate-y-0 scale-100 opacity-100" },
    { name: "Sake Bomb", tags: "Japanese • 4.8 ★", style: "z-20 translate-y-[-1rem] scale-95 opacity-60" },
    { name: "Rustic Hearth", tags: "Italian • 4.7 ★", style: "z-10 translate-y-[-2rem] scale-90 opacity-30" }
  ];
  const [restaurants, setRestaurants] = useState(initialRestaurants);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setRestaurants(prev => {
        const newArr = [...prev];
        const last = newArr.pop();
        newArr.unshift(last);
        return newArr;
      });
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  // --- Feature 2: Order Telemetry Logic ---
  const telemetryMessages = [
    "Order received via Dish Dash",
    "Kitchen confirmed ticket #8402",
    "Chef has started preparation",
    "Quality check passed",
    "Driver assigned (ETA: 12 min)",
    "Out for delivery"
  ];
  const [telemetryLines, setTelemetryLines] = useState([]);
  
  useEffect(() => {
    const defaultMessages = audience === 'customer' ? [
      "Order received via Dish Dash",
      "Kitchen confirmed ticket #8402",
      "Chef has started preparation",
      "Quality check passed",
      "Driver assigned (ETA: 12 min)",
      "Out for delivery"
    ] : [
      "New order received: #8402",
      "Auto-accepting via Dish Dash API",
      "Sending prep time to customer",
      "Assigning driver (Courier arrives in 5m)",
      "Order successfully handed off",
      "Revenue added: $42.50"
    ];
    let index = 0;
    const interval = setInterval(() => {
      setTelemetryLines(prev => {
        const newLines = [...prev, defaultMessages[index]];
        if (newLines.length > 5) newLines.shift();
        return newLines;
      });
      index++;
      if (index >= telemetryMessages.length) {
        clearInterval(interval);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  // --- GSAP Scrolling Logic ---
  useEffect(() => {
    let ctx = gsap.context(() => {
      
      // 1. Navbar Morphing
      ScrollTrigger.create({
        start: 'top -50',
        end: 99999,
        toggleClass: { className: 'bg-background/80 md:w-[60%] border-white/20 shadow-2xl', targets: '#navbar' }
      });

      // 2. Hero Text Fade-Up
      if (heroTextRef.current) {
        gsap.from(heroTextRef.current.children, {
          y: 40,
          opacity: 0,
          duration: 1,
          stagger: 0.1,
          ease: "power3.out",
          delay: 0.2
        });
      }

      // 3. Philosophy Text Reveal
      if (philosophyTextRef.current) {
         gsap.from(philosophyTextRef.current.children, {
           scrollTrigger: {
             trigger: "#philosophy",
             start: "top center",
           },
           y: 50,
           opacity: 0,
           duration: 1.2,
           stagger: 0.2,
           ease: "power3.out"
         });
      }

      // 4. Protocol Sticky Stacking Steps
      // We clear any existing scroll triggers first
      ScrollTrigger.getAll().forEach(st => {
         if(st.vars.id && st.vars.id.startsWith('card-')) {
             st.kill();
         }
      });

      protocolCardsRef.current.forEach((card, index) => {
        if (!card) return;
        
        ScrollTrigger.create({
          trigger: card,
          start: "top top+=120",
          endTrigger: "#protocol",
          end: "bottom bottom",
          pin: true,
          pinSpacing: false,
          id: `card-${index}`,
        });

        // Fade out previous cards when this one comes in
        if (index > 0) {
          gsap.to(protocolCardsRef.current[index - 1], {
            scrollTrigger: {
              trigger: card,
              start: "top center+=250",
              end: "top top+=120",
              scrub: true,
            },
            scale: 0.92,
            opacity: 0.3,
            filter: "blur(10px)",
          });
        }
      });

    }, mainRef);
    return () => ctx.revert();
  }, []);

  return (
    <main ref={mainRef} className="bg-primary text-background min-h-screen font-sans selection:bg-accent selection:text-primary overflow-x-hidden">
      {/* 
        Aesthetic Preset: Midnight Bistro
        Palette: Obsidian #0D0D12, Gold #C9A84C, Ivory #FAF8F5, Slate #2A2A35
        Typography: Inter (sans), Playfair Display (drama), JetBrains Mono (data)
      */}
      
      {/* A. NAVBAR */}
      <nav id="navbar" className="fixed top-6 left-1/2 -translate-x-1/2 w-[90%] max-w-5xl rounded-full z-50 flex items-center justify-between px-6 py-4 transition-all duration-300 bg-background/5 backdrop-blur-md border border-white/10">
        <div className="text-xl font-bold tracking-tight text-background">Dish Dash</div>
        <div className="hidden md:flex items-center gap-8 font-mono text-sm uppercase tracking-widest text-background/70">
          <a href="#features" className="hover:text-accent transition-colors">Features</a>
          <a href="#philosophy" className="hover:text-accent transition-colors">Philosophy</a>
          <a href="#protocol" className="hover:text-accent transition-colors">Protocol</a>
          
          <button 
             onClick={() => setAudience(a => a === 'customer' ? 'restaurant' : 'customer')}
             className={`ml-4 px-4 py-1.5 rounded-full border transition-colors ${audience === 'restaurant' ? 'border-accent text-accent bg-accent/10' : 'border-white/20 hover:border-accent hover:text-accent'}`}
          >
             {audience === 'customer' ? 'For Restaurants' : 'For Customers'}
          </button>
        </div>
        <button 
           className="relative group overflow-hidden rounded-full px-6 py-2 bg-accent text-primary font-bold hover:scale-[1.03] transition-transform duration-300"
           onClick={() => window.location.href = "/auth/login"}
        >
          <span className="relative z-10">{audience === 'customer' ? 'Order Now' : 'Partner Dashboard'}</span>
        </button>
      </nav>

      <div className="fixed top-0 left-0 w-full h-[15vh] bg-gradient-to-b from-primary to-transparent z-40 pointer-events-none"></div>

      {/* B. HERO SECTION */}
      <section className="relative h-[100dvh] w-full flex items-end pb-24 px-8 md:px-16 overflow-hidden">
        {/* Background Image */}
        <div className="absolute inset-0 z-0 bg-primary">
          <img 
            src="https://images.unsplash.com/photo-1514933651103-005eec06c04b?q=80&w=2574&auto=format&fit=crop" 
            alt="Hero Background Customer" 
            className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-1000 ${audience === 'customer' ? 'opacity-60' : 'opacity-0'}`}
          />
          <img 
            src="https://images.unsplash.com/photo-1556155092-490a1ba16284?q=80&w=2070&auto=format&fit=crop" 
            alt="Hero Background Restaurant" 
            className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-1000 ${audience === 'restaurant' ? 'opacity-60' : 'opacity-0'}`}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-primary via-primary/80 to-transparent z-10"></div>
        </div>

        {/* Hero Content */}
        <div ref={heroTextRef} className="relative z-10 max-w-4xl hero-content">
          <h1 className="flex flex-col gap-2">
            <span className="text-2xl md:text-3xl font-bold tracking-tight text-accent uppercase font-sans">
              {audience === 'customer' ? 'Gourmet discovery meets' : 'Elevate your restaurant with'}
            </span>
            <span className="text-6xl md:text-8xl font-drama italic text-background leading-[0.9] pb-4 block min-h-[1.1em]">
               {audience === 'customer' ? 'Precision delivery.' : 'Seamless logistics.'}
            </span>
          </h1>
          <p className="mt-8 text-lg md:text-xl text-background/80 max-w-lg font-sans leading-relaxed min-h-[3rem]">
            {audience === 'customer' ? 'Dish Dash. The smartest way to discover and order from local restaurants.' : 'Partner with Dish Dash to access exclusive clientele, manage menus dynamically, and preserve your margins.'}
          </p>
          <div className="mt-12">
            <button 
              onClick={() => window.location.href = "/auth/register"}
              className="group relative overflow-hidden rounded-[2rem] px-8 py-4 bg-accent text-primary font-bold text-lg hover:scale-[1.03] transition-all duration-300 flex items-center gap-3"
            >
              <span className="relative z-10">{audience === 'customer' ? 'Start Ordering' : 'Become a Partner'}</span>
              <ArrowRight className="relative z-10 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>
      </section>

      {/* C. FEATURES - Interactive Functional Artifacts */}
      <section id="features" className="py-32 px-8 md:px-16 bg-primary">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Card 1: Restaurant Shuffler */}
          <div className="bg-textDark/30 border border-white/5 rounded-[2rem] p-8 h-[400px] flex flex-col justify-between hover:-translate-y-1 transition-transform duration-300">
            <div>
              <h3 className="text-xl font-bold font-sans text-background collapse-tight">
                {audience === 'customer' ? 'Curated Local Restaurants' : 'Premium Brand Placement'}
              </h3>
              <p className="text-background/60 mt-2 text-sm">
                {audience === 'customer' ? 'Hand-picked eateries near you, with authentic reviews.' : 'Get featured to high-value customers looking for culinary excellence.'}
              </p>
            </div>
            {/* Shuffler UI Mockup */}
            <div className="relative h-48 w-full mt-8">
              {restaurants.map((rest, i) => (
                <div 
                  key={rest.name}
                  className={`absolute inset-x-0 bottom-4 bg-[#1A1A24] border border-white/10 rounded-2xl p-4 shadow-2xl flex items-center gap-4 transition-all duration-700 ease-[cubic-bezier(0.34,1.56,0.64,1)] ${rest.style}`}
                  style={{
                    zIndex: i === 0 ? 30 : i === 1 ? 20 : 10,
                    transform: `translateY(${i === 0 ? '0' : i === 1 ? '-1rem' : '-2rem'}) scale(${i === 0 ? 1 : i === 1 ? 0.95 : 0.9})`,
                    opacity: i === 0 ? 1 : i === 1 ? 0.6 : 0.3
                  }}
                >
                  <div className="w-12 h-12 rounded-full bg-accent/20 flex items-center justify-center text-accent shadow-[0_0_15px_rgba(201,168,76,0.2)]"><Star className="w-6 h-6 fill-current"/></div>
                  <div><div className="font-bold text-background">{rest.name}</div><div className="text-xs text-background/60">{rest.tags}</div></div>
                </div>
              ))}
            </div>
          </div>

          {/* Card 2: Order Telemetry */}
          <div className="bg-textDark/30 border border-white/5 rounded-[2rem] p-8 h-[400px] flex flex-col justify-between hover:-translate-y-1 transition-transform duration-300">
             <div>
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 rounded-full bg-accent animate-pulse"></div>
                <span className="text-xs font-mono uppercase tracking-widest text-accent">Live Feed</span>
              </div>
              <h3 className="text-xl font-bold font-sans text-background collapse-tight">
                {audience === 'customer' ? 'Real-Time Order Tracking' : 'Kitchen Intelligence'}
              </h3>
              <p className="text-background/60 mt-2 text-sm">
                {audience === 'customer' ? 'Watch your meal from kitchen to doorstep.' : 'Deep analytics and live order injection straight to your line.'}
              </p>
            </div>
            <div className="bg-[#0A0A0F] border border-white/5 rounded-xl p-5 font-mono text-xs text-background/80 h-48 overflow-hidden flex flex-col justify-end shadow-inner relative">
              <div className="absolute top-0 left-0 w-full h-8 bg-gradient-to-b from-[#0A0A0F] to-transparent z-10"></div>
              {telemetryLines.map((line, i) => (
                 <div key={i} className={`py-1 ${i === telemetryLines.length - 1 ? 'text-accent flex items-center gap-2 font-bold' : ''}`} style={{ opacity: 0.3 + (i * 0.15) }}>
                    <span className="text-accent/50 mr-2">&gt;</span>{line}
                    {i === telemetryLines.length - 1 && <span className="w-2 h-3 bg-accent animate-pulse inline-block ml-1"></span>}
                 </div>
              ))}
            </div>
          </div>

          {/* Card 3: Delivery Scheduler */}
          <div className="bg-textDark/30 border border-white/5 rounded-[2rem] p-8 h-[400px] flex flex-col justify-between hover:-translate-y-1 transition-transform duration-300">
            <div>
              <h3 className="text-xl font-bold font-sans text-background collapse-tight">
                 {audience === 'customer' ? 'Exclusive Daily Deals' : 'Dynamic Menu Offerings'}
              </h3>
              <p className="text-background/60 mt-2 text-sm">
                 {audience === 'customer' ? 'Special discounts and offers you won\'t find elsewhere.' : 'Control pricing and availability based on your inventory in real-time.'}
              </p>
            </div>
            <div className="mt-8 relative">
                <div className="grid grid-cols-7 gap-2 text-center text-xs font-mono mb-2 text-background/50">
                  <div>S</div><div>M</div><div>T</div><div>W</div><div>T</div><div>F</div><div>S</div>
                </div>
                <div className="grid grid-cols-7 gap-2">
                  {[...Array(14)].map((_, i) => (
                    <div key={i} className={`h-8 rounded-md flex items-center justify-center border font-mono text-xs ${i === 4 ? 'bg-accent/20 border-accent text-accent shadow-[0_0_10px_rgba(201,168,76,0.5)]' : 'border-white/5 bg-textDark/20 text-background/30'}`}>
                      {i === 4 ? '-20%' : ''}
                    </div>
                  ))}
                </div>
                <div className="mt-4 w-full bg-accent/10 border border-accent/30 text-accent rounded-lg py-2 text-center font-mono text-sm">
                  Activate Offer
                </div>
            </div>
          </div>
        </div>
      </section>

      {/* D. PHILOSOPHY */}
      <section id="philosophy" className="relative h-[80vh] flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 z-0 bg-primary">
          <img 
            src="https://images.unsplash.com/photo-1414235077428-33898f82204e?q=80&w=2070&auto=format&fit=crop" 
            alt="Philosophy Texture Customer" 
            className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-1000 ${audience === 'customer' ? 'opacity-10' : 'opacity-0'}`}
          />
          <img 
            src="https://images.unsplash.com/photo-1572656306390-40a9fc3899f7?q=80&w=2070&auto=format&fit=crop" 
            alt="Philosophy Texture Restaurant" 
            className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-1000 ${audience === 'restaurant' ? 'opacity-10' : 'opacity-0'}`}
            onError={(e) => { e.target.style.display = 'none'; }}
          />
        </div>
        <div ref={philosophyTextRef} className="relative z-10 max-w-4xl text-center px-8">
          <p className="text-background/50 text-xl md:text-2xl font-sans mb-6">
            {audience === 'customer' ? 'Most food ordering focuses on:' : 'Most platforms focus on:'} <span className="line-through">{audience === 'customer' ? 'speed over quality' : 'crushing your margins'}</span>.
          </p>
          <h2 className="text-5xl md:text-7xl font-drama italic text-background leading-tight">
            We focus on: <br/><span className="text-accent not-italic font-sans font-bold tracking-tight">{audience === 'customer' ? 'culinary excellence' : 'your profitability'}</span>.
          </h2>
        </div>
      </section>

      {/* E. PROTOCOL - Sticky Stacking Steps */}
      <section id="protocol" className="py-32 px-8 md:px-16 bg-primary text-background relative">
         <div className="max-w-4xl mx-auto py-16 text-center">
            <h2 className="text-4xl font-bold uppercase tracking-tight mb-4 text-background">
               {audience === 'customer' ? 'The Dish Dash Protocol' : 'The Partner Pipeline'}
            </h2>
            <p className="text-background/60 font-mono">
               {audience === 'customer' ? 'How we orchestrate your meal.' : 'How we integrate with your kitchen.'}
            </p>
         </div>

         {/* Steps will be implemented via CSS/GSAP later, scaffolding blocks for now */}
         <div className="max-w-3xl mx-auto space-y-[40vh] pb-[20vh] relative z-10">
            
            <div ref={el => protocolCardsRef.current[0] = el} className="bg-[#12121A] border border-white/5 rounded-[3rem] p-12 shadow-[0_20px_50px_rgba(0,0,0,0.5)] flex flex-col md:flex-row gap-12 items-center protocol-card transform origin-top w-full">
              <div className="w-32 h-32 rounded-full border-2 border-accent/20 bg-accent/5 flex items-center justify-center flex-shrink-0 shadow-[0_0_30px_rgba(201,168,76,0.1)]">
                 <MapPin className="w-12 h-12 text-accent" strokeWidth={1.5} />
              </div>
              <div>
                <div className="font-mono text-accent font-bold mb-2">STEP 01</div>
                <h3 className="text-3xl font-bold mb-4 text-background">{audience === 'customer' ? 'Discover' : 'Setup Profile'}</h3>
                <p className="text-lg text-background/60 leading-relaxed">
                   {audience === 'customer' ? 'Browse our curated selection of top-tier local eateries. Real reviews, authentic experiences. No endless scrolling.' : 'Create your restaurant profile, upload mouth-watering images using our integrated CDN, and build your digital menu in minutes.'}
                </p>
              </div>
            </div>

            <div ref={el => protocolCardsRef.current[1] = el} className="bg-[#12121A] border border-white/5 rounded-[3rem] p-12 shadow-[0_20px_50px_rgba(0,0,0,0.5)] flex flex-col md:flex-row gap-12 items-center protocol-card transform origin-top w-full mt-8">
              <div className="w-32 h-32 rounded-full border-2 border-accent/20 bg-accent/5 flex items-center justify-center flex-shrink-0 shadow-[0_0_30px_rgba(201,168,76,0.1)]">
                 <Clock className="w-12 h-12 text-accent" strokeWidth={1.5} />
               </div>
              <div>
                <div className="font-mono text-accent font-bold mb-2">STEP 02</div>
                <h3 className="text-3xl font-bold mb-4 text-background">{audience === 'customer' ? 'Order & Track' : 'Receive & Fulfill'}</h3>
                <p className="text-lg text-background/60 leading-relaxed">
                   {audience === 'customer' ? 'Place your order securely. Our live telemetry keeps you connected from the kitchen directly to your front door.' : 'Orders stream into your dedicated Partner Dashboard immediately. Manage statuses and keep your customers informed effortlessly.'}
                </p>
              </div>
            </div>

            <div ref={el => protocolCardsRef.current[2] = el} className="bg-[#12121A] border border-white/5 rounded-[3rem] p-12 shadow-[0_20px_50px_rgba(0,0,0,0.5)] flex flex-col md:flex-row gap-12 items-center protocol-card transform origin-top w-full mt-8">
              <div className="w-32 h-32 rounded-full border-2 border-accent/20 bg-accent/5 flex items-center justify-center flex-shrink-0 shadow-[0_0_30px_rgba(201,168,76,0.1)]">
                 <Star className="w-12 h-12 text-accent" strokeWidth={1.5} />
              </div>
              <div>
                <div className="font-mono text-accent font-bold mb-2">STEP 03</div>
                <h3 className="text-3xl font-bold mb-4 text-background">{audience === 'customer' ? 'Enjoy & Review' : 'Grow & Analyze'}</h3>
                <p className="text-lg text-background/60 leading-relaxed">
                   {audience === 'customer' ? 'Experience exceptional dining at home. Share your thoughts to help the community discover hidden gems.' : 'Monitor your performance through deep analytics and authentic review aggregations. Scale your operation profitably.'}
                </p>
              </div>
            </div>

         </div>
      </section>

      {/* G. FOOTER */}
      <footer className="bg-[#050508] text-background pt-24 pb-8 px-8 md:px-16 rounded-t-[4rem] mt-[-2rem] relative z-20">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
          <div className="md:col-span-2">
            <h2 className="text-3xl font-bold mb-4">Dish Dash</h2>
            <p className="text-background/50 max-w-sm">The smartest way to discover and order from local restaurants. Delivering culinary excellence.</p>
          </div>
          <div>
            <h4 className="font-mono text-accent mb-6">Platform</h4>
            <ul className="space-y-4 text-background/60">
              <li><a href="#" className="hover:text-background transition-colors">Restaurants</a></li>
              <li><a href="#" className="hover:text-background transition-colors">Deals</a></li>
              <li><a href="#" className="hover:text-background transition-colors">Partner with us</a></li>
            </ul>
          </div>
          <div>
             <h4 className="font-mono text-accent mb-6">Legal</h4>
            <ul className="space-y-4 text-background/60">
              <li><a href="#" className="hover:text-background transition-colors">Privacy</a></li>
              <li><a href="#" className="hover:text-background transition-colors">Terms</a></li>
            </ul>
          </div>
        </div>
        <div className="max-w-7xl mx-auto border-t border-white/10 pt-8 flex flex-col md:flex-row items-center justify-between">
          <div className="text-background/40 text-sm mb-4 md:mb-0">© 2026 Dish Dash. All rights reserved.</div>
          <div className="flex items-center gap-3 bg-textDark/30 rounded-full px-4 py-2 border border-white/5">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span className="font-mono text-xs uppercase tracking-widest text-background/70">Order system online</span>
          </div>
        </div>
      </footer>

    </main>
  );
}
