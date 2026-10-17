export type Page = "Home" | "Marketplace" | "Prices" | "Schemes" | "My Farm" | "Ask KisanSetu" | "Crop Health" | "Legal Aid" | "Settings";

export const listings = [
  { id: 1, crop: "Tomatoes", hindi: "टमाटर", variety: "Fresh harvest · Grade A", quantity: 42, price: 1850, location: "Sonipat, Haryana", distance: "28 km", date: "Available today", image: "https://images.unsplash.com/photo-1546094096-0df4bcaaa337?auto=format&fit=crop&w=800&q=85", seller: "Ramesh Kumar", bids: 4, tag: "4 offers received" },
  { id: 2, crop: "Potatoes", hindi: "आलू", variety: "Farm sorted · Medium size", quantity: 80, price: 1250, location: "Meerut, Uttar Pradesh", distance: "54 km", date: "Available tomorrow", image: "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=800&q=85", seller: "Suresh Pal", bids: 2, tag: "2 offers received" },
  { id: 3, crop: "Onions", hindi: "प्याज़", variety: "Dry onion · Well cured", quantity: 35, price: 2200, location: "Gurugram, Haryana", distance: "19 km", date: "Available in 2 days", image: "https://images.unsplash.com/photo-1508747703725-719777637510?auto=format&fit=crop&w=800&q=85", seller: "Sunita Devi", bids: 3, tag: "Popular near you" },
  { id: 4, crop: "Wheat", hindi: "गेहूँ", variety: "Cleaned grain", quantity: 120, price: 2425, location: "Baghpat, Uttar Pradesh", distance: "67 km", date: "Available today", image: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=800&q=85", seller: "Demo farmer", bids: 1, tag: "DEMO LISTING" }
];

export const schemes = [
  { id: 1, name: "PM-KISAN", category: "Income support", status: "Check eligibility", description: "Income support scheme for eligible landholding farmer families.", why: "Could be relevant based on your farmer profile and land records.", documents: ["Aadhaar", "Land record", "Bank account details"], source: "https://pmkisan.gov.in/", updated: "Verify current rules on the official portal" },
  { id: 2, name: "Kisan Credit Card (KCC)", category: "Agricultural credit", status: "Potential match", description: "Credit access for eligible farmers to support cultivation and related needs.", why: "May fit if you cultivate land and meet the participating bank's criteria.", documents: ["Identity proof", "Land/cultivation documents", "Bank application"], source: "https://www.myscheme.gov.in/", updated: "Check current eligibility and bank terms" },
  { id: 3, name: "Pradhan Mantri Fasal Bima Yojana", category: "Crop insurance", status: "Check season", description: "Crop insurance scheme subject to notified crops, areas and enrollment windows.", why: "Relevance depends on your crop, district, season and current notification.", documents: ["Land/cultivation proof", "Sowing details", "Bank details if required"], source: "https://pmfby.gov.in/", updated: "Season and district notification required" }
];

export const prices = [
  { crop: "Tomato", mandi: "Azadpur Mandi", price: 1850, change: 4.2, date: "18 Oct 2026" },
  { crop: "Potato", mandi: "Ghaziabad Mandi", price: 1250, change: -1.4, date: "18 Oct 2026" },
  { crop: "Onion", mandi: "Ghazipur Mandi", price: 2200, change: 2.8, date: "18 Oct 2026" }
];

export const priceHistory = [
  { day: "12 Oct", price: 1640, forecast: null },
  { day: "13 Oct", price: 1690, forecast: null },
  { day: "14 Oct", price: 1660, forecast: null },
  { day: "15 Oct", price: 1740, forecast: null },
  { day: "16 Oct", price: 1780, forecast: 1780 },
  { day: "17 Oct", price: 1810, forecast: 1810 },
  { day: "18 Oct", price: 1850, forecast: 1850 },
  { day: "19 Oct", price: null, forecast: 1870 },
  { day: "20 Oct", price: null, forecast: 1830 },
  { day: "21 Oct", price: null, forecast: 1900 },
  { day: "22 Oct", price: null, forecast: 1880 }
];
