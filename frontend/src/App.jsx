import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ArrowRight, Clock, Star, MapPin } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

export default function App() {
  const mainRef = useRef(null);

  // --- Feature 1: Restaurant Shuffler Logic ---
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
    let index = 0;
    const interval = setInterval(() => {
      setTelemetryLines(prev => {
        const newLines = [...prev, telemetryMessages[index]];
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
      // Animations will go here
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
        </div>
        <button className="relative group overflow-hidden rounded-full px-6 py-2 bg-accent text-primary font-bold hover:scale-[1.03] transition-transform duration-300">
          <span className="relative z-10">Find Restaurants</span>
        </button>
      </nav>

      <div className="fixed top-0 left-0 w-full h-[15vh] bg-gradient-to-b from-primary to-transparent z-40 pointer-events-none"></div>

      {/* B. HERO SECTION */}
      <section className="relative h-[100dvh] w-full flex items-end pb-24 px-8 md:px-16 overflow-hidden">
        {/* Background Image */}
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1514933651103-005eec06c04b?q=80&w=2574&auto=format&fit=crop" 
            alt="Midnight Bistro Atmosphere" 
            className="w-full h-full object-cover opacity-60"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-primary via-primary/80 to-transparent"></div>
        </div>

        {/* Hero Content */}
        <div className="relative z-10 max-w-4xl hero-content">
          <h1 className="flex flex-col gap-2">
            <span className="text-2xl md:text-3xl font-bold tracking-tight text-accent uppercase font-sans">
              Gourmet discovery meets
            </span>
            <span className="text-6xl md:text-8xl font-drama italic text-background leading-[0.9] pb-4">
              Precision delivery.
            </span>
          </h1>
          <p className="mt-8 text-lg md:text-xl text-background/80 max-w-lg font-sans leading-relaxed">
            Dish Dash. The smartest way to discover and order from local restaurants.
          </p>
          <div className="mt-12">
            <button className="group relative overflow-hidden rounded-[2rem] px-8 py-4 bg-accent text-primary font-bold text-lg hover:scale-[1.03] transition-all duration-300 flex items-center gap-3">
              <span className="relative z-10">Order Now</span>
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
              <h3 className="text-xl font-bold font-sans text-background collapse-tight">Curated Local Restaurants</h3>
              <p className="text-background/60 mt-2 text-sm">Hand-picked eateries near you, with authentic reviews.</p>
            </div>
            {/* Shuffler UI Mockup */}
            <div className="relative h-48 w-full mt-8">
              {restaurants.map((rest, i) => (
                <div 
                  key={rest.name}
                  className={`absolute inset-x-0 bottom-4 bg-textDark rounded-2xl p-4 shadow-xl flex items-center gap-4 transition-all duration-700 ease-[cubic-bezier(0.34,1.56,0.64,1)] ${rest.style}`}
                  style={{
                    zIndex: i === 0 ? 30 : i === 1 ? 20 : 10,
                    transform: `translateY(${i === 0 ? '0' : i === 1 ? '-1rem' : '-2rem'}) scale(${i === 0 ? 1 : i === 1 ? 0.95 : 0.9})`,
                    opacity: i === 0 ? 1 : i === 1 ? 0.6 : 0.3
                  }}
                >
                  <div className="w-12 h-12 rounded-full bg-accent/20 flex items-center justify-center text-accent"><Star className="w-6 h-6 fill-current"/></div>
                  <div><div className="font-bold">{rest.name}</div><div className="text-xs text-background/60">{rest.tags}</div></div>
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
              <h3 className="text-xl font-bold font-sans text-background collapse-tight">Real-Time Order Tracking</h3>
              <p className="text-background/60 mt-2 text-sm">Watch your meal from kitchen to doorstep.</p>
            </div>
            <div className="bg-[#050508] rounded-xl p-4 font-mono text-xs text-background/80 h-40 overflow-hidden flex flex-col justify-end">
              {telemetryLines.map((line, i) => (
                 <div key={i} className={`${i === telemetryLines.length - 1 ? 'text-accent flex items-center gap-2' : ''}`} style={{ opacity: 0.4 + (i * 0.15) }}>
                    &gt; {line}
                    {i === telemetryLines.length - 1 && <span className="w-2 h-3 bg-accent animate-pulse inline-block"></span>}
                 </div>
              ))}
            </div>
          </div>

          {/* Card 3: Delivery Scheduler */}
          <div className="bg-textDark/30 border border-white/5 rounded-[2rem] p-8 h-[400px] flex flex-col justify-between hover:-translate-y-1 transition-transform duration-300">
            <div>
              <h3 className="text-xl font-bold font-sans text-background collapse-tight">Exclusive Daily Deals</h3>
              <p className="text-background/60 mt-2 text-sm">Special discounts and offers you won't find elsewhere.</p>
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
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1414235077428-33898f82204e?q=80&w=2070&auto=format&fit=crop" 
            alt="Gourmet Plating" 
            className="w-full h-full object-cover opacity-10"
          />
        </div>
        <div className="relative z-10 max-w-4xl text-center px-8">
          <p className="text-background/50 text-xl md:text-2xl font-sans mb-6">
            Most food ordering focuses on: <span className="line-through">speed over quality</span>.
          </p>
          <h2 className="text-5xl md:text-7xl font-drama italic text-background leading-tight">
            We focus on: <br/><span className="text-accent not-italic font-sans font-bold tracking-tight">culinary excellence</span>.
          </h2>
        </div>
      </section>

      {/* E. PROTOCOL - Sticky Stacking Steps */}
      <section id="protocol" className="py-24 px-8 md:px-16 bg-background text-primary">
         <div className="max-w-4xl mx-auto py-24 text-center">
            <h2 className="text-4xl font-bold uppercase tracking-tight mb-4">The Dish Dash Protocol</h2>
            <p className="text-primary/60 font-mono">How we orchestrate your meal.</p>
         </div>

         {/* Steps will be implemented via CSS/GSAP later, scaffolding blocks for now */}
         <div className="max-w-3xl mx-auto space-y-32 pb-32">
            
            <div className="bg-white rounded-[3rem] p-12 shadow-2xl flex flex-col md:flex-row gap-12 items-center protocol-card">
              <div className="w-32 h-32 rounded-full border-2 border-primary/10 flex items-center justify-center flex-shrink-0">
                 <MapPin className="w-12 h-12 text-primary" strokeWidth={1.5} />
              </div>
              <div>
                <div className="font-mono text-accent font-bold mb-2">STEP 01</div>
                <h3 className="text-3xl font-bold mb-4">Discover</h3>
                <p className="text-lg text-primary/70">Browse our curated selection of top-tier local eateries. Real reviews, authentic experiences.</p>
              </div>
            </div>

            <div className="bg-white rounded-[3rem] p-12 shadow-2xl flex flex-col md:flex-row gap-12 items-center protocol-card">
              <div className="w-32 h-32 rounded-full border-2 border-primary/10 flex items-center justify-center flex-shrink-0">
                 <Clock className="w-12 h-12 text-primary" strokeWidth={1.5} />
              </div>
              <div>
                <div className="font-mono text-accent font-bold mb-2">STEP 02</div>
                <h3 className="text-3xl font-bold mb-4">Order & Track</h3>
                <p className="text-lg text-primary/70">Place your order securely. Out live telemetry keeps you connected from the kitchen to your door.</p>
              </div>
            </div>

            <div className="bg-white rounded-[3rem] p-12 shadow-2xl flex flex-col md:flex-row gap-12 items-center protocol-card">
              <div className="w-32 h-32 rounded-full border-2 border-primary/10 flex items-center justify-center flex-shrink-0">
                 <Star className="w-12 h-12 text-primary" strokeWidth={1.5} />
              </div>
              <div>
                <div className="font-mono text-accent font-bold mb-2">STEP 03</div>
                <h3 className="text-3xl font-bold mb-4">Enjoy & Review</h3>
                <p className="text-lg text-primary/70">Experience exceptional dining at home. Share your thoughts to help the community.</p>
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
