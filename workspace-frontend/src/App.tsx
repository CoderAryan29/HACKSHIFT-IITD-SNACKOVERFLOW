import { useMemo, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import {
  Sprout, LayoutDashboard, Store, TrendingUp, Landmark, MoreHorizontal,
  Search, Bell, MapPin, ChevronDown, ArrowUpRight, ArrowRight, Plus,
  Filter, Heart, MessageCircle, CheckCircle2, Clock3, ShieldCheck,
  Tractor, Leaf, FileText, Wallet, ChartNoAxesCombined, Handshake,
  Camera, Menu, X, Languages, ChevronRight, MapPinned, Package,
  ClipboardCheck, CircleHelp, Send, CalendarDays, SlidersHorizontal,
  BadgeCheck, ExternalLink, Check, Upload, Image as ImageIcon, UserRound,
  Scale, Banknote, Sprout as CropIcon
} from "lucide-react";
import { listings, prices, priceHistory, schemes, type Page } from "./data";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import CropHealthPage from "./CropHealthPage";

const nav: { label: Page; icon: any; group?: string }[] = [
  { label: "Home", icon: LayoutDashboard },
  { label: "Marketplace", icon: Store },
  { label: "Prices", icon: TrendingUp },
  { label: "Schemes", icon: Landmark },
  { label: "My Farm", icon: Sprout },
  { label: "Ask KisanSetu", icon: MessageCircle },
  { label: "Crop Health", icon: Leaf },
  { label: "Legal Aid", icon: Scale },
  { label: "Settings", icon: MoreHorizontal }
];

function money(n: number) { return "₹" + n.toLocaleString("en-IN"); }

export default function App() {
  const [page, setPage] = useState<Page>("Home");
  const [mobileMenu, setMobileMenu] = useState(false);
  const [language, setLanguage] = useState<"EN" | "हिं">("EN");
  const [role, setRole] = useState<"farmer" | "buyer">("farmer");
  const [toast, setToast] = useState("");
  const [search, setSearch] = useState("");
  const [cropFilter, setCropFilter] = useState("All crops");
  const [showListingForm, setShowListingForm] = useState(false);
  const [selectedListing, setSelectedListing] = useState<number | null>(null);
  const [offerListing, setOfferListing] = useState<number | null>(null);
  const [listingCrop, setListingCrop] = useState("Tomatoes");
  const [listingQty, setListingQty] = useState("40");
  const [listingPrice, setListingPrice] = useState("1850");
  const [listingDate, setListingDate] = useState("2026-10-19");
  const [myListings, setMyListings] = useState<typeof listings>([]);
  const [bidAmount, setBidAmount] = useState("1950");
  const [activeScheme, setActiveScheme] = useState<number | null>(null);
  const [profileStep, setProfileStep] = useState(1);
  const [profile, setProfile] = useState({ state: "Uttar Pradesh", district: "Meerut", land: "2.5", ownership: "Owner", crops: ["Wheat", "Potato"], age: "35–60" });
  const [schemeResults, setSchemeResults] = useState(false);
  const [schemeSearch, setSchemeSearch] = useState("");
  const [showMore, setShowMore] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<{from: string; text: string}[]>([
    { from: "assistant", text: "Namaste! I can help you compare market offers, understand scheme eligibility, or plan your next farm decision. What would you like to explore?" }
  ]);
  const [legalType, setLegalType] = useState("Unpaid crop sale");
  const [legalDistrict, setLegalDistrict] = useState("Meerut");
  const [legalDone, setLegalDone] = useState(false);
  const [ledgerTab, setLedgerTab] = useState("Overview");

  const filteredListings = useMemo(() => [...myListings, ...listings].filter(x => {
    const matchesSearch = `${x.crop} ${x.location} ${x.seller}`.toLowerCase().includes(search.toLowerCase());
    const matchesCrop = cropFilter === "All crops" || x.crop === cropFilter;
    return matchesSearch && matchesCrop;
  }), [search, cropFilter, myListings]);

  function notify(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(""), 2800);
  }
  function go(next: Page) {
    setPage(next);
    setMobileMenu(false);
    setShowMore(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  function publishListing(e: React.FormEvent) {
    e.preventDefault();
    const newItem = {
      id: Date.now(), crop: listingCrop, hindi: listingCrop === "Tomatoes" ? "टमाटर" : listingCrop === "Potatoes" ? "आलू" : "प्याज़",
      variety: "Your new listing", quantity: Number(listingQty), price: Number(listingPrice),
      location: `${profile.district}, ${profile.state}`, distance: "Your area", date: `Available ${listingDate}`,
      image: listingCrop === "Tomatoes" ? listings[0].image : listingCrop === "Potatoes" ? listings[1].image : listings[2].image,
      seller: "Your farm", bids: 0, tag: "YOUR LISTING"
    };
    setMyListings(prev => [newItem, ...prev]);
    setShowListingForm(false);
    notify("Listing created in this demo. No live buyer notification was sent.");
  }
  function submitBid(e: React.FormEvent) {
    e.preventDefault();
    setOfferListing(null);
    notify(`Demo bid of ${money(Number(bidAmount))}/quintal submitted. No real deal was created.`);
  }
  function submitChat(e: React.FormEvent) {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const question = chatInput.trim();
    setChatMessages(prev => [...prev, { from: "user", text: question }, { from: "assistant", text: "I can help with that. This prototype uses demo responses; connect the KisanSetu agent API to receive verified, personalized guidance. For now, compare current dated prices and check the official source before making a decision." }]);
    setChatInput("");
  }
  const isHi = language === "हिं";
  const titleFor = (label: Page) => isHi ? ({ Home: "होम", Marketplace: "बाज़ार", Prices: "भाव", Schemes: "सरकारी योजनाएँ", "My Farm": "मेरा खेत", "Ask KisanSetu": "किसानसेतु से पूछें", "Crop Health": "फसल स्वास्थ्य", "Legal Aid": "कानूनी सहायता", Settings: "और" } as any)[label] : label;

  return (
    <div className="app">
      <aside className={`sidebar ${mobileMenu ? "sidebar-open" : ""}`}>
        <div className="brand" onClick={() => go("Home")} role="button" tabIndex={0}>
          <div className="brand-mark"><Sprout size={23} /></div>
          <div><strong>KisanSetu</strong><span>BETTER MARKETS, BETTER HARVESTS</span></div>
          <button className="icon-btn close-mobile" onClick={(e) => { e.stopPropagation(); setMobileMenu(false); }} aria-label="Close menu"><X /></button>
        </div>
        <div className="workspace-label">YOUR FARM WORKSPACE</div>
        <nav className="nav-list">
          {nav.slice(0, 5).map(item => <NavItem key={item.label} item={item} active={page === item.label} onClick={() => go(item.label)} title={titleFor(item.label)} />)}
          <div className="nav-divider" />
          <div className="workspace-label">SUPPORT & TOOLS</div>
          {nav.slice(5, 8).map(item => <NavItem key={item.label} item={item} active={page === item.label} onClick={() => go(item.label)} title={titleFor(item.label)} />)}
        </nav>
        <div className="sidebar-bottom">
          <div className="help-card"><div className="help-icon"><CircleHelp size={18}/></div><strong>Need a hand?</strong><p>Get help with selling, schemes or your farm records.</p><button onClick={() => go("Ask KisanSetu")}>Ask KisanSetu <ArrowRight size={14}/></button></div>
          <button className={`nav-item ${page === "Settings" ? "active" : ""}`} onClick={() => go("Settings")}><MoreHorizontal size={18}/><span>{titleFor("Settings")}</span></button>
          <div className="user-mini"><div className="avatar">RK</div><div className="user-copy"><strong>Ramesh Kumar</strong><span>Farmer account · Demo</span></div><ChevronDown size={16}/></div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <button className="icon-btn mobile-menu-btn" onClick={() => setMobileMenu(true)} aria-label="Open navigation"><Menu /></button>
          <div className="breadcrumb"><span>Workspace</span><ChevronRight size={14}/><strong>{titleFor(page)}</strong></div>
          <div className="top-actions">
            <div className="location-pill"><MapPin size={15}/><span>{profile.district}, {profile.state}</span><ChevronDown size={13}/></div>
            <button className="language-btn" onClick={() => setLanguage(language === "EN" ? "हिं" : "EN")}><Languages size={16}/>{language}</button>
            <button className="icon-btn notification-btn" aria-label="Notifications" onClick={() => notify("No new notifications in this demo.")}><Bell size={18}/><i /></button>
            <button className="avatar top-avatar" onClick={() => go("Settings")} aria-label="Open profile">RK</button>
          </div>
        </header>

        <div className="page-content">
          <AnimatePresence mode="wait">
            <motion.div key={page} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -5 }} transition={{ duration: 0.18 }}>
              {page === "Home" && <HomePage go={go} notify={notify} role={role} setRole={setRole} />}
              {page === "Marketplace" && <MarketplacePage listings={filteredListings} search={search} setSearch={setSearch} cropFilter={cropFilter} setCropFilter={setCropFilter} showListingForm={showListingForm} setShowListingForm={setShowListingForm} selectedListing={selectedListing} setSelectedListing={setSelectedListing} offerListing={offerListing} setOfferListing={setOfferListing} listingCrop={listingCrop} setListingCrop={setListingCrop} listingQty={listingQty} setListingQty={setListingQty} listingPrice={listingPrice} setListingPrice={setListingPrice} listingDate={listingDate} setListingDate={setListingDate} publishListing={publishListing} bidAmount={bidAmount} setBidAmount={setBidAmount} submitBid={submitBid} role={role} setRole={setRole} notify={notify} />}
              {page === "Prices" && <PricesPage go={go} notify={notify} />}
              {page === "Schemes" && <SchemesPage profile={profile} setProfile={setProfile} profileStep={profileStep} setProfileStep={setProfileStep} results={schemeResults} setResults={setSchemeResults} activeScheme={activeScheme} setActiveScheme={setActiveScheme} search={schemeSearch} setSearch={setSchemeSearch} />}
              {page === "My Farm" && <FarmPage tab={ledgerTab} setTab={setLedgerTab} notify={notify} />}
              {page === "Ask KisanSetu" && <ChatPage messages={chatMessages} input={chatInput} setInput={setChatInput} submit={submitChat} />}
              {page === "Crop Health" && <CropHealthPage />}
              {page === "Legal Aid" && <LegalPage type={legalType} setType={setLegalType} district={legalDistrict} setDistrict={setLegalDistrict} done={legalDone} setDone={setLegalDone} />}
              {page === "Settings" && <SettingsPage language={language} setLanguage={setLanguage} role={role} setRole={setRole} profile={profile} setProfile={setProfile} notify={notify} />}
            </motion.div>
          </AnimatePresence>
        </div>
        <footer className="footer"><span>© 2026 KisanSetu</span><span>Built for better farming decisions <Sprout size={13}/></span><span>Demo data is clearly labelled</span></footer>
      </main>

      <nav className="mobile-bottom">
        {(["Home", "Marketplace", "Prices", "Schemes", "Settings"] as Page[]).map(label => {
          const Icon = nav.find(n => n.label === label)?.icon || MoreHorizontal;
          return <button key={label} className={page === label ? "mobile-active" : ""} onClick={() => go(label)}><Icon size={19}/><span>{label === "Marketplace" ? "Market" : label === "Schemes" ? "Schemes" : label === "Settings" ? "More" : label}</span></button>;
        })}
      </nav>
      <AnimatePresence>{toast && <motion.div className="toast" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }}><CheckCircle2 size={18}/>{toast}</motion.div>}</AnimatePresence>
    </div>
  );
}

function NavItem({ item, active, onClick, title }: { item: {label: Page; icon: any}; active: boolean; onClick: () => void; title: string }) {
  const Icon = item.icon;
  return <button className={`nav-item ${active ? "active" : ""}`} onClick={onClick}><Icon size={18}/><span>{title}</span>{active && <span className="active-dot" />}</button>;
}

function PageHeader({ eyebrow, title, subtitle, action }: { eyebrow?: string; title: string; subtitle: string; action?: React.ReactNode }) {
  return <div className="page-heading"><div>{eyebrow && <div className="eyebrow">{eyebrow}</div>}<h1>{title}</h1><p>{subtitle}</p></div>{action && <div className="heading-action">{action}</div>}</div>;
}
function Button({ children, onClick, variant = "primary", icon }: { children: React.ReactNode; onClick?: () => void; variant?: "primary" | "secondary" | "ghost"; icon?: React.ReactNode }) {
  return <button className={`btn btn-${variant}`} onClick={onClick}>{icon}{children}</button>;
}
function SectionTitle({ title, detail, action }: { title: string; detail?: string; action?: React.ReactNode }) {
  return <div className="section-title"><div><h2>{title}</h2>{detail && <p>{detail}</p>}</div>{action}</div>;
}

function HomePage({ go, notify, role, setRole }: { go: (p: Page) => void; notify: (s:string)=>void; role: "farmer"|"buyer"; setRole: (r:"farmer"|"buyer")=>void }) {
  return <div className="page-stack">
    <PageHeader eyebrow="SUNDAY, 18 OCTOBER 2026" title="Namaste, Ramesh 👋" subtitle="Your farm's market, offers and support in one place." action={<div className="role-toggle"><button className={role==="farmer"?"selected":""} onClick={()=>setRole("farmer")}>Farmer view</button><button className={role==="buyer"?"selected":""} onClick={()=>setRole("buyer")}>Buyer view</button></div>} />
    <section className="market-hero">
      <div className="hero-copy"><div className="hero-kicker"><span className="pulse-dot"/> YOUR MARKET OPPORTUNITY</div><h2>{role === "farmer" ? "Your next sale could start here." : "Find produce that fits your business."}</h2><p>{role === "farmer" ? "Compare buyer offers with mandi prices, understand your net return, and choose what works for your farm." : "Browse nearby produce, compare quantities and prices, and make a competitive offer."}</p><div className="hero-actions"><Button onClick={() => go("Marketplace")} icon={<Store size={17}/>}>{role === "farmer" ? "Compare buyer offers" : "Browse produce"}</Button><Button variant="secondary" onClick={() => go("Prices")} icon={<TrendingUp size={17}/>}>Check mandi prices</Button></div><div className="hero-trust"><span><ShieldCheck size={14}/> Transparent comparisons</span><span><MapPinned size={14}/> Delhi-NCR + UP demo region</span></div></div>
      <div className="hero-visual"><div className="hero-photo" /><div className="floating-price"><span className="floating-label">AZADPUR MANDI · DEMO</span><strong>₹1,850<span>/qtl</span></strong><span className="positive"><ArrowUpRight size={14}/> 4.2% in sample data</span></div><div className="floating-note"><div className="mini-icon"><Handshake size={17}/></div><div><strong>Buyer offers, side by side</strong><span>Compare before you decide</span></div></div></div>
    </section>
    <section className="metric-grid">
      <Metric icon={<Store/>} label="Produce listings" value="128" sub="Demo marketplace" tone="green"/>
      <Metric icon={<Handshake/>} label="Buyer offers" value="24" sub="Simulated bids" tone="gold"/>
      <Metric icon={<TrendingUp/>} label="Market snapshot" value="3 crops" sub="Prices dated 18 Oct" tone="blue"/>
      <Metric icon={<Landmark/>} label="Scheme matches" value="3 to review" sub="Not approval guarantees" tone="soil"/>
    </section>
    <div className="content-grid home-grid">
      <section className="panel"><SectionTitle title="Market snapshot" detail="Sample reference prices · 18 Oct 2026" action={<button className="text-link" onClick={() => go("Prices")}>View prices <ArrowRight size={15}/></button>}/><div className="market-table">{prices.map((p) => <div className="market-row" key={p.crop}><div className={`crop-dot ${p.crop.toLowerCase()}`}>{p.crop==="Tomato"?"T":p.crop==="Potato"?"P":"O"}</div><div className="market-name"><strong>{p.crop}</strong><span>{p.mandi}</span></div><div className="market-price"><strong>{money(p.price)}</strong><span>per quintal</span></div><div className={`change ${p.change>0?"up":"down"}`}>{p.change>0?"+":""}{p.change}%</div></div>)}</div><div className="notice-line"><Clock3 size={14}/> Demo reference data only. Confirm the latest price before selling.</div></section>
      <section className="panel opportunity-panel"><SectionTitle title="A useful next step" detail="Based on your current setup"/><div className="opportunity-icon"><Landmark size={22}/></div><span className="soft-badge">PERSONALIZED SUPPORT</span><h3>Check which government schemes may fit your farm</h3><p>Review possible matches, missing information and documents using your profile.</p><Button onClick={() => go("Schemes")} icon={<ArrowRight size={16}/>}>Check schemes for me</Button><div className="mini-separator"/><div className="support-link" onClick={() => go("Crop Health")} role="button" tabIndex={0}><div className="mini-icon"><Leaf size={17}/></div><div><strong>Need to check a crop?</strong><span>Open Crop Health tools</span></div><ChevronRight size={18}/></div></section>
    </div>
    <section className="panel"><SectionTitle title="Opportunities near your area" detail="Illustrative listings from the demo marketplace" action={<button className="text-link" onClick={() => go("Marketplace")}>Explore marketplace <ArrowRight size={15}/></button>}/><div className="listing-grid">{listings.slice(0,3).map(l => <ListingCard key={l.id} item={l} onClick={() => go("Marketplace")}/>)}</div></section>
    <section className="bottom-cta"><div className="cta-symbol"><Wallet size={25}/></div><div><h3>Know what your sale is really worth.</h3><p>Compare a buyer's offer with a dated mandi reference and estimated costs.</p></div><Button onClick={() => go("Prices")}>Compare net prices <ArrowRight size={16}/></Button></section>
  </div>;
}

function Metric({ icon, label, value, sub, tone }: {icon: React.ReactNode; label:string; value:string; sub:string; tone:string}) {
  return <div className="metric-card"><div className={`metric-icon ${tone}`}>{icon}</div><div><span>{label}</span><strong>{value}</strong><small>{sub}</small></div></div>;
}
function ListingCard({ item, onClick }: {item: typeof listings[number]; onClick:()=>void}) {
  return <button className="listing-card" onClick={onClick}><div className="listing-image" style={{backgroundImage:`url(${item.image})`}}><span className="listing-tag">{item.tag}</span><span className="heart-btn"><Heart size={16}/></span></div><div className="listing-body"><div className="listing-top"><h3>{item.crop}</h3><span>{item.quantity} qtl</span></div><p>{item.variety}</p><div className="listing-price">{money(item.price)} <small>/ quintal</small></div><div className="listing-meta"><span><MapPin size={13}/>{item.location}</span><span><Clock3 size={13}/>{item.date}</span></div><div className="listing-footer"><span>{item.bids} offers / bids</span><span className="arrow-circle"><ArrowUpRight size={16}/></span></div></div></button>;
}

function MarketplacePage(props: any) {
  const { listings: items, search, setSearch, cropFilter, setCropFilter, showListingForm, setShowListingForm, selectedListing, setSelectedListing, offerListing, setOfferListing, listingCrop, setListingCrop, listingQty, setListingQty, listingPrice, setListingPrice, listingDate, setListingDate, publishListing, bidAmount, setBidAmount, submitBid, role, setRole, notify } = props;
  const selected = items.find((x:any) => x.id === selectedListing);
  return <div className="page-stack">
    <PageHeader eyebrow="FARMER ↔ BUYER MARKETPLACE" title="A better deal starts with a clear comparison." subtitle="Browse produce, list your harvest, and compare offers before you commit." action={<Button onClick={() => setShowListingForm(true)} icon={<Plus size={17}/>}>Create listing</Button>}/>
    <div className="marketplace-banner"><div className="banner-icon"><Handshake size={23}/></div><div><strong>One market. More choices.</strong><p>Compare asking prices, buyer bids and mandi references separately. Demo listings and simulated bids are labelled.</p></div><div className="role-toggle"><button className={role==="farmer"?"selected":""} onClick={()=>setRole("farmer")}>Farmer</button><button className={role==="buyer"?"selected":""} onClick={()=>setRole("buyer")}>Buyer</button></div></div>
    <div className="toolbar"><div className="search-box"><Search size={17}/><input value={search} onChange={(e:any)=>setSearch(e.target.value)} placeholder="Search crop, buyer or location"/></div><select value={cropFilter} onChange={(e:any)=>setCropFilter(e.target.value)}><option>All crops</option><option>Tomatoes</option><option>Potatoes</option><option>Onions</option><option>Wheat</option></select><button className="btn btn-secondary" onClick={()=>notify("Advanced filters are a UI demo; wire them to listing query parameters.")}><SlidersHorizontal size={16}/> Filters</button><div className="toolbar-spacer"/><span className="result-count">{items.length} listings</span></div>
    <div className="market-tabs"><button className="tab-active">Browse produce</button><button onClick={()=>notify("Your bids view is a demo placeholder until connected to the backend.")}>My bids</button><button onClick={()=>notify("Your listings appear here after creation in this demo.")}>My listings</button><button onClick={()=>notify("Deals will appear here after backend integration.")}>Deals</button></div>
    {showListingForm && <div className="modal-backdrop"><motion.form initial={{opacity:0,y:12}} animate={{opacity:1,y:0}} className="modal-card" onSubmit={publishListing}><div className="modal-head"><div><span className="eyebrow">NEW MARKETPLACE LISTING</span><h2>Sell your produce</h2><p>Preview fields are saved locally in this demo.</p></div><button type="button" className="icon-btn" onClick={()=>setShowListingForm(false)}><X/></button></div><div className="form-grid"><label>Crop<select value={listingCrop} onChange={e=>setListingCrop(e.target.value)}><option>Tomatoes</option><option>Potatoes</option><option>Onions</option></select></label><label>Quantity (quintals)<input type="number" min="1" required value={listingQty} onChange={e=>setListingQty(e.target.value)}/></label><label>Expected price (₹/quintal)<input type="number" min="1" required value={listingPrice} onChange={e=>setListingPrice(e.target.value)}/></label><label>Available date<input type="date" required value={listingDate} onChange={e=>setListingDate(e.target.value)}/></label></div><div className="upload-placeholder"><Upload size={20}/><strong>Photo upload placeholder</strong><span>Connect image upload to the backend/storage bucket.</span></div><div className="modal-actions"><Button variant="secondary" onClick={()=>setShowListingForm(false)}>Cancel</Button><button className="btn btn-primary" type="submit"><Plus size={16}/> Publish demo listing</button></div></motion.form></div>}
    {selected && <div className="modal-backdrop"><motion.div initial={{opacity:0,y:12}} animate={{opacity:1,y:0}} className="modal-card"><div className="modal-head"><div><span className="eyebrow">LISTING DETAILS</span><h2>{selected.crop}</h2><p>{selected.quantity} quintals · {selected.location}</p></div><button className="icon-btn" onClick={()=>setSelectedListing(null)}><X/></button></div><div className="detail-price-row"><div><span>Asking price</span><strong>{money(selected.price)}<small>/qtl</small></strong></div><div><span>Mandi reference · demo</span><strong>{money(selected.crop==="Tomatoes"?1850:selected.crop==="Potatoes"?1250:2200)}<small>/qtl</small></strong></div></div><p className="muted-copy">The asking price and mandi reference are different values. Transport costs and requested quantity may change net proceeds.</p><div className="offer-row"><div className="buyer-avatar">MB</div><div><strong>Metro Buyers <span className="demo-pill">DEMO BUYER</span></strong><span>Simulated buyer · pickup terms not connected</span></div><strong>{money(selected.price+100)}/qtl</strong></div><Button onClick={()=>{setSelectedListing(null);setOfferListing(selected.id)}}>Place a demo bid <ArrowRight size={16}/></Button></motion.div></div>}
    {offerListing !== null && <div className="modal-backdrop"><motion.form initial={{opacity:0,y:12}} animate={{opacity:1,y:0}} className="modal-card" onSubmit={submitBid}><div className="modal-head"><div><span className="eyebrow">SIMULATED BUYER OFFER</span><h2>Place a bid</h2><p>This is a local UI demo, not a real offer.</p></div><button type="button" className="icon-btn" onClick={()=>setOfferListing(null)}><X/></button></div><label className="field-label">Your bid (₹ per quintal)<input type="number" min="1" value={bidAmount} onChange={e=>setBidAmount(e.target.value)} required/></label><div className="notice-line"><ShieldCheck size={15}/> Review quantity and delivery terms before accepting a real deal.</div><div className="modal-actions"><Button variant="secondary" onClick={()=>setOfferListing(null)}>Cancel</Button><button className="btn btn-primary" type="submit">Submit demo bid</button></div></motion.form></div>}
    {items.length ? <div className="listing-grid">{items.map((item:any)=><div key={item.id} className="listing-wrap"><ListingCard item={item} onClick={()=>setSelectedListing(item.id)}/><button className="listing-detail-link" onClick={()=>setSelectedListing(item.id)}>View offer details <ArrowRight size={14}/></button></div>)}</div> : <Empty icon={<Search/>} title="No matching produce" detail="Try another crop or location."/>}
    <div className="notice-line"><ShieldCheck size={15}/> Prices and listings shown here are illustrative demo data, not live market quotes.</div>
  </div>;
}

function PricesPage({ go, notify }: {go:(p:Page)=>void; notify:(s:string)=>void}) {
  const [crop,setCrop] = useState("Tomato");
  const [mandi,setMandi] = useState("All mandis");
  const [qty,setQty] = useState("40");
  const [offer,setOffer] = useState("1950");
  const [transport,setTransport] = useState("450");
  const net = Number(offer) * Number(qty) - Number(transport);
  return <div className="page-stack">
    <PageHeader eyebrow="PRICE INTELLIGENCE" title="Compare the price. Then decide." subtitle="Separate buyer offers, mandi references and estimated net proceeds before choosing where to sell."/>
    <div className="filter-panel"><label>Crop<select value={crop} onChange={e=>setCrop(e.target.value)}><option>Tomato</option><option>Potato</option><option>Onion</option></select></label><label>Mandi<select value={mandi} onChange={e=>setMandi(e.target.value)}><option>All mandis</option><option>Azadpur Mandi</option><option>Ghaziabad Mandi</option><option>Ghazipur Mandi</option></select></label><div className="filter-context"><MapPin size={15}/> Delhi-NCR + Uttar Pradesh demo region</div></div>
    <div className="price-card-grid">{prices.filter(p=>p.crop===crop || crop==="Tomato" && p.crop==="Tomato").map(p=><div className="price-card" key={p.crop}><div className="price-card-head"><div className="crop-dot tomato">{p.crop[0]}</div><span className="soft-badge">DEMO REFERENCE</span></div><span className="muted-label">{p.mandi}</span><strong className="big-price">{money(p.price)}<small>/quintal</small></strong><span className={`change ${p.change>0?"up":"down"}`}>{p.change>0?"+":""}{p.change}% in sample data</span><div className="price-card-foot">Observed: {p.date}</div></div>)}</div>
    <div className="content-grid price-layout"><section className="panel chart-panel"><SectionTitle title={`${crop} price trend`} detail="Illustrative chart · not a live forecast"/><div className="chart-legend"><span><i className="legend-dot observed"/>Observed sample</span><span><i className="legend-dot forecast"/>Illustrative projection</span></div><div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><AreaChart data={priceHistory} margin={{top:10,right:10,left:0,bottom:0}}><defs><linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#2e7d32" stopOpacity={0.18}/><stop offset="100%" stopColor="#2e7d32" stopOpacity={0}/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" stroke="#e8ede5"/><XAxis dataKey="day" tick={{fontSize:11,fill:"#728073"}} axisLine={false} tickLine={false}/><YAxis tick={{fontSize:11,fill:"#728073"}} axisLine={false} tickLine={false} width={54}/><Tooltip formatter={(value:any)=>value===null?"—":`₹${value}/qtl`}/><Area type="monotone" dataKey="price" stroke="#2e7d32" strokeWidth={2.5} fill="url(#priceFill)" connectNulls={false}/><Area type="monotone" dataKey="forecast" stroke="#d39a17" strokeWidth={2} strokeDasharray="5 4" fill="none" connectNulls={false}/></AreaChart></ResponsiveContainer></div><div className="notice-line"><Clock3 size={14}/> Illustrative values only. No live forecast or market API is connected.</div></section>
      <section className="panel net-panel"><SectionTitle title="Estimate your net proceeds" detail="Change assumptions to compare a buyer offer."/><div className="form-stack"><label>Buyer offer (₹/quintal)<input type="number" value={offer} onChange={e=>setOffer(e.target.value)}/></label><label>Quantity (quintals)<input type="number" value={qty} onChange={e=>setQty(e.target.value)}/></label><label>Estimated transport cost (₹ total)<input type="number" value={transport} onChange={e=>setTransport(e.target.value)}/></label></div><div className="net-result"><span>Estimated net proceeds</span><strong>{money(net)}</strong><small>Assumes all listed quantity is sold at the entered offer, less the entered transport cost.</small></div><Button onClick={()=>notify("Estimate updated locally. This is not a guaranteed sale value.")}>Save comparison <Check size={16}/></Button><button className="text-link" onClick={()=>go("Marketplace")}>Compare with marketplace offers <ArrowRight size={15}/></button></section></div>
    <div className="notice-line"><ShieldCheck size={15}/> A higher gross offer is not always better. Check quantity, transport, pickup terms and payment terms.</div>
  </div>;
}

function SchemesPage(props:any) {
  const {profile,setProfile,profileStep,setProfileStep,results,setResults,activeScheme,setActiveScheme,search,setSearch} = props;
  const filtered = schemes.filter(s=>`${s.name} ${s.category} ${s.description}`.toLowerCase().includes(search.toLowerCase()));
  function toggleCrop(crop:string){setProfile((p:any)=>({...p,crops:p.crops.includes(crop)?p.crops.filter((x:string)=>x!==crop):[...p.crops,crop]}));}
  return <div className="page-stack">
    <PageHeader eyebrow="PERSONALIZED GOVERNMENT SUPPORT" title="Find schemes that may fit your farm." subtitle="Answer a few questions to see possible matches, missing details and official next steps."/>
    <div className="schemes-intro"><div className="schemes-intro-icon"><Landmark size={25}/></div><div><h3>Benefits are personal. Eligibility is rule-based.</h3><p>Recommendations depend on your location, landholding, crops and the rules available to KisanSetu. A match is not a guarantee of approval.</p></div><div className="official-stamp"><ShieldCheck size={18}/><span>Official sources<br/>shown on each scheme</span></div></div>
    <div className="scheme-layout">
      <section className="panel scheme-wizard"><div className="wizard-head"><div><span className="eyebrow">YOUR FARM PROFILE</span><h2>Check schemes for me</h2><p>Only provide details relevant to the rules being checked.</p></div><span className="step-count">STEP {profileStep} OF 3</span></div><div className="progress-track"><span style={{width:`${profileStep/3*100}%`}}/></div>
      {profileStep===1 && <div className="form-stack"><label>State<select value={profile.state} onChange={e=>setProfile({...profile,state:e.target.value})}><option>Uttar Pradesh</option><option>Haryana</option><option>Delhi</option><option>Punjab</option><option>Rajasthan</option></select></label><label>District<input value={profile.district} onChange={e=>setProfile({...profile,district:e.target.value})} placeholder="Enter district"/></label><label>Landholding area (acres)<input type="number" min="0" step=".1" value={profile.land} onChange={e=>setProfile({...profile,land:e.target.value})}/></label><label>Land / cultivation status<select value={profile.ownership} onChange={e=>setProfile({...profile,ownership:e.target.value})}><option>Owner</option><option>Tenant</option><option>Sharecropper</option><option>Other</option></select></label><div className="form-actions"><Button onClick={()=>setProfileStep(2)}>Continue <ArrowRight size={16}/></Button></div></div>}
      {profileStep===2 && <div className="form-stack"><label>Which crops do you grow?</label><div className="crop-select-grid">{["Wheat","Potato","Tomato","Onion","Rice","Sugarcane"].map(c=><button type="button" key={c} className={`crop-choice ${profile.crops.includes(c)?"chosen":""}`} onClick={()=>toggleCrop(c)}>{profile.crops.includes(c)&&<Check size={14}/>} {c}</button>)}</div><label>Age range (only used if a scheme requires it)<select value={profile.age} onChange={e=>setProfile({...profile,age:e.target.value})}><option>Under 18</option><option>18–35</option><option>35–60</option><option>Over 60</option><option>Prefer not to say</option></select></label><div className="notice-line"><ShieldCheck size={14}/> Sensitive optional fields are not requested by default.</div><div className="form-actions split"><Button variant="secondary" onClick={()=>setProfileStep(1)}>Back</Button><Button onClick={()=>setProfileStep(3)}>Review <ArrowRight size={16}/></Button></div></div>}
      {profileStep===3 && <div className="review-box"><div className="review-line"><span>Location</span><strong>{profile.district}, {profile.state}</strong></div><div className="review-line"><span>Landholding</span><strong>{profile.land || "Not provided"} acres · {profile.ownership}</strong></div><div className="review-line"><span>Crops</span><strong>{profile.crops.join(", ") || "Not selected"}</strong></div><div className="review-line"><span>Age range</span><strong>{profile.age}</strong></div><p className="muted-copy">This prototype uses illustrative matching explanations. It does not run the official scheme eligibility rules.</p><div className="form-actions split"><Button variant="secondary" onClick={()=>setProfileStep(2)}>Back</Button><Button onClick={()=>{setResults(true);setProfileStep(3)}}>Show possible matches <ArrowRight size={16}/></Button></div></div>}
      <div className="privacy-note"><ShieldCheck size={15}/><span>Your profile should only be used for relevant matching. Connect the real eligibility engine before treating results as authoritative.</span></div></section>
      <section className="scheme-results"><div className="results-head"><div><span className="eyebrow">SCHEME EXPLORER</span><h2>{results?"Possible matches for your profile":"Browse available schemes"}</h2><p>{results?"Review the reasons, required documents and official source.":"Browse seeded examples while the rules engine is being connected."}</p></div><span className="result-count">{filtered.length} examples</span></div><div className="search-box scheme-search"><Search size={16}/><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search schemes or support type"/></div>{filtered.map((s,i)=><div className={`scheme-card ${activeScheme===s.id?"scheme-expanded":""}`} key={s.id}><button className="scheme-card-top" onClick={()=>setActiveScheme(activeScheme===s.id?null:s.id)}><div className="scheme-logo"><Landmark size={20}/></div><div className="scheme-main"><span className="scheme-category">{s.category}</span><h3>{s.name}</h3><p>{s.description}</p></div><ChevronDown className={activeScheme===s.id?"rotate":""} size={18}/></button><div className="scheme-status-row"><span className={`status-pill ${results?"status-review":"status-neutral"}`}>{results?(i===0?"Needs verification":i===1?"Potential match":"Check season"):s.status}</span><span className="muted-label">Source needs verification</span></div>{activeScheme===s.id&&<div className="scheme-details"><div><strong>Why this may be relevant</strong><p>{s.why}</p></div><div><strong>Documents to review</strong><ul>{s.documents.map(d=><li key={d}>{d}</li>)}</ul></div><div className="source-row"><span>Official portal / scheme information</span><a href={s.source} target="_blank" rel="noreferrer">Open source <ExternalLink size={13}/></a></div><p className="small-warning">This is a demo explanation, not an official eligibility verdict. Confirm the current rules on the linked portal.</p></div>}</div>)}</section>
    </div>
  </div>;
}

function FarmPage({tab,setTab,notify}:{tab:string;setTab:(s:string)=>void;notify:(s:string)=>void}) {
  const [entries,setEntries] = useState([{date:"16 Oct 2026",category:"Fertiliser",note:"Wheat crop",amount:2400},{date:"12 Oct 2026",category:"Labour",note:"Field preparation",amount:1800},{date:"09 Oct 2026",category:"Seeds",note:"Potato season",amount:3200}]);
  const [show,setShow] = useState(false);
  const [amount,setAmount] = useState("1000");
  const [category,setCategory] = useState("Seeds");
  const [note,setNote] = useState("");
  function add(e:React.FormEvent){e.preventDefault();setEntries(prev=>[{date:"Today",category,note:note||"Farm expense",amount:Number(amount)},...prev]);setShow(false);notify("Expense added to local demo ledger.");}
  return <div className="page-stack"><PageHeader eyebrow="YOUR FARM BUSINESS" title="Your farm, clearly accounted for." subtitle="Keep an eye on expenses, sales and the records behind your decisions." action={<Button onClick={()=>setShow(true)} icon={<Plus size={16}/>}>Add entry</Button>}/><div className="metric-grid"><Metric icon={<Wallet/>} label="Recorded expenses" value={money(entries.reduce((s,e)=>s+e.amount,0))} sub="Local demo ledger" tone="green"/><Metric icon={<Banknote/>} label="Recorded sales" value="₹24,500" sub="Illustrative sample" tone="gold"/><Metric icon={<ChartNoAxesCombined/>} label="Net estimate" value={money(24500-entries.reduce((s,e)=>s+e.amount,0))} sub="Sales minus listed expenses" tone="blue"/><Metric icon={<Package/>} label="Active crops" value="2" sub="Wheat · Potato" tone="soil"/></div><div className="panel"><div className="market-tabs"><button className={tab==="Overview"?"tab-active":""} onClick={()=>setTab("Overview")}>Overview</button><button className={tab==="Ledger"?"tab-active":""} onClick={()=>setTab("Ledger")}>Khata / ledger</button><button className={tab==="Sales"?"tab-active":""} onClick={()=>setTab("Sales")}>Sales & deals</button></div>{tab==="Overview"&&<div className="farm-overview"><div className="farm-summary"><div className="large-farm-icon"><Tractor size={26}/></div><div><h3>Ramesh's farm</h3><p>Meerut, Uttar Pradesh · 2.5 acres · Demo profile</p><span className="soft-badge">PROFILE NEEDS CONFIRMATION</span></div><Button variant="secondary" onClick={()=>notify("Profile editing will connect to the real account API.")}>Edit profile</Button></div><div className="farm-stat-grid"><div><span>Main crops</span><strong>Wheat, Potato</strong></div><div><span>Landholding</span><strong>2.5 acres</strong></div><div><span>Latest activity</span><strong>Expense entry</strong></div></div></div>}{tab==="Ledger"&&<div className="ledger-table"><div className="ledger-head"><span>Date</span><span>Category / note</span><span>Amount</span></div>{entries.map((e,i)=><div className="ledger-row" key={i}><span>{e.date}</span><div><strong>{e.category}</strong><small>{e.note}</small></div><strong>{money(e.amount)}</strong></div>)}</div>}{tab==="Sales"&&<Empty icon={<Handshake/>} title="No connected deals yet" detail="Accepted marketplace deals will appear here after backend integration."/>}</div>{show&&<div className="modal-backdrop"><form className="modal-card" onSubmit={add}><div className="modal-head"><div><span className="eyebrow">FARM KHATA</span><h2>Add an expense</h2></div><button type="button" className="icon-btn" onClick={()=>setShow(false)}><X/></button></div><div className="form-stack"><label>Category<select value={category} onChange={e=>setCategory(e.target.value)}><option>Seeds</option><option>Fertiliser</option><option>Pesticide</option><option>Labour</option><option>Water</option><option>Machinery</option><option>Other</option></select></label><label>Amount (₹)<input type="number" min="1" value={amount} onChange={e=>setAmount(e.target.value)} required/></label><label>Note<input value={note} onChange={e=>setNote(e.target.value)} placeholder="What was this expense for?"/></label></div><div className="modal-actions"><Button variant="secondary" onClick={()=>setShow(false)}>Cancel</Button><button type="submit" className="btn btn-primary">Save demo entry</button></div></form></div>}</div>;
}

function ChatPage({messages,input,setInput,submit}:{messages:{from:string;text:string}[];input:string;setInput:(s:string)=>void;submit:(e:React.FormEvent)=>void}) {
  return <div className="page-stack"><PageHeader eyebrow="YOUR FARM ASSISTANT" title="Ask KisanSetu." subtitle="Get help understanding market choices, farm records and relevant support."/><div className="chat-layout"><aside className="panel chat-aside"><div className="assistant-avatar"><Sprout size={24}/></div><h3>Your farm decision assistant</h3><p>Ask about market prices, comparing offers or understanding a scheme. Responses here are demo placeholders until the agent API is connected.</p><div className="chat-suggestion-list"><button onClick={()=>setInput("How do I compare a buyer offer with mandi price?")}>Compare buyer vs mandi price <ArrowRight size={14}/></button><button onClick={()=>setInput("Which documents should I check for a government scheme?")}>Scheme documents <ArrowRight size={14}/></button><button onClick={()=>setInput("How should I estimate net proceeds after transport?")}>Estimate net proceeds <ArrowRight size={14}/></button></div></aside><section className="panel chat-window"><div className="chat-head"><div className="assistant-avatar small"><Sprout size={18}/></div><div><strong>KisanSetu Assistant</strong><span><i className="online-dot"/> Demo mode · Not connected to live agent</span></div></div><div className="chat-messages">{messages.map((m,i)=><div className={`chat-message ${m.from==="user"?"message-user":""}`} key={i}><div className="message-avatar">{m.from==="user"?<UserRound size={16}/>:<Sprout size={16}/>}</div><div className="message-bubble">{m.text}</div></div>)}</div><form className="chat-compose" onSubmit={submit}><input value={input} onChange={e=>setInput(e.target.value)} placeholder="Ask about prices, offers or schemes…"/><button className="send-btn" aria-label="Send message"><Send size={17}/></button></form><p className="chat-disclaimer">Check official sources and dated prices before making financial decisions.</p></section></div></div>;
}

function LegalPage({type,setType,district,setDistrict,done,setDone}:{type:string;setType:(s:string)=>void;district:string;setDistrict:(s:string)=>void;done:boolean;setDone:(b:boolean)=>void}) {
  return <div className="page-stack"><PageHeader eyebrow="LEGAL AID NAVIGATOR" title="Understand your options and where to get help." subtitle="A guided legal-information flow for Uttar Pradesh. This is information, not legal advice."/><div className="legal-layout"><section className="panel"><div className="legal-heading"><div className="legal-icon"><Scale size={22}/></div><div><h2>Tell us what happened</h2><p>Share only the details needed to guide the next step.</p></div></div>{!done?<div className="form-stack"><label>Type of dispute<select value={type} onChange={e=>setType(e.target.value)}><option>Unpaid crop sale</option><option>Land boundary dispute</option><option>Tenancy or inheritance</option><option>Loan harassment</option><option>False land claim</option></select></label><label>District<input value={district} onChange={e=>setDistrict(e.target.value)}/></label><label>Urgency<select><option>Routine</option><option>Time-sensitive</option><option>Immediate threat or violence</option></select></label><Button onClick={()=>setDone(true)}>Prepare information checklist <ArrowRight size={16}/></Button></div>:<div className="legal-answer"><span className="soft-badge">DEMO GUIDANCE</span><h3>Suggested information to gather</h3><p>For: {type} · {district}, Uttar Pradesh</p><ul><li>Keep copies of agreements, receipts and relevant messages.</li><li>Write down dates, parties involved and what remains unresolved.</li><li>Check the relevant local office or seek advice from a qualified lawyer before filing.</li></ul><div className="notice-line">Legal information, not legal advice. Ask a lawyer to review documents before filing.</div><a className="official-link" href="https://nalsa.gov.in/" target="_blank" rel="noreferrer">National Legal Services Authority <ExternalLink size={14}/></a><Button variant="secondary" onClick={()=>setDone(false)}>Edit answers</Button></div>}</section><aside className="panel legal-emergency"><div className="legal-icon"><ShieldCheck size={22}/></div><h3>Need urgent help?</h3><p>If someone is in immediate danger, contact emergency services first.</p><div className="emergency-number">112</div><span>India emergency number</span><div className="mini-separator"/><strong>Free legal assistance depends on eligibility.</strong><p>Ask the District Legal Services Authority or visit the official NALSA site for current information.</p></aside></div></div>;
}

function SettingsPage({language,setLanguage,role,setRole,profile,setProfile,notify}:any) {
  return <div className="page-stack"><PageHeader eyebrow="PROFILE & PREFERENCES" title="Make KisanSetu work for you." subtitle="Manage your demo profile, language and marketplace role."/><div className="settings-grid"><section className="panel"><div className="settings-profile"><div className="avatar settings-avatar">RK</div><div><h2>Ramesh Kumar</h2><p>Demo profile · Meerut, Uttar Pradesh</p></div><span className="demo-pill">DEMO</span></div><div className="settings-form"><label>Preferred language<select value={language} onChange={e=>setLanguage(e.target.value)}><option value="EN">English</option><option value="हिं">हिन्दी (Hindi)</option></select></label><label>Marketplace role<select value={role} onChange={e=>setRole(e.target.value)}><option value="farmer">Farmer</option><option value="buyer">Buyer</option></select></label><label>State<select value={profile.state} onChange={e=>setProfile({...profile,state:e.target.value})}><option>Uttar Pradesh</option><option>Haryana</option><option>Delhi</option><option>Punjab</option><option>Rajasthan</option></select></label><label>District<input value={profile.district} onChange={e=>setProfile({...profile,district:e.target.value})}/></label><label>Landholding (acres)<input type="number" value={profile.land} onChange={e=>setProfile({...profile,land:e.target.value})}/></label><Button onClick={()=>notify("Settings updated for this browser session only.")}>Save preferences <Check size={16}/></Button></div></section><section className="panel"><SectionTitle title="Privacy & trust" detail="Prototype controls and disclosures"/><div className="privacy-list"><div><ShieldCheck/><span><strong>Personalized scheme matching</strong><small>Use only fields required by scheme rules; sensitive optional fields need consent.</small></span></div><div><Banknote/><span><strong>Market information</strong><small>Prices in this prototype are illustrative and must not be treated as live quotes.</small></span></div><div><UserRound/><span><strong>Demo identity</strong><small>This frontend does not authenticate a real user yet.</small></span></div></div><div className="notice-line">Connect Firebase and backend authorization before using real farmer records.</div></section></div></div>;
}

function Empty({icon,title,detail}:{icon:React.ReactNode;title:string;detail:string}) {
  return <div className="empty-state"><div className="empty-icon">{icon}</div><h3>{title}</h3><p>{detail}</p></div>;
}
