import { useState } from "react";
import { ArrowLeft, Crosshair, LoaderCircle, MapPin, Sprout, Store } from "lucide-react";
import type { AccountProfile, AccountRole, QuestionnaireAnswers } from "./auth-api";
import "./questionnaire-page.css";

interface QuestionnairePageProps {
  role: AccountRole;
  profile: AccountProfile | null;
  defaultName: string;
  isSaving: boolean;
  error: string | null;
  onSave: (answers: QuestionnaireAnswers) => Promise<void>;
  onSkip: () => Promise<void>;
  onBack: () => void;
}

const cropOptions = ["Wheat", "Rice", "Potato", "Tomato", "Onion", "Sugarcane", "Cotton", "Other"];
const buyerOptions = ["Wheat", "Rice", "Potato", "Tomato", "Onion", "Pulses", "Fruits", "Other"];

export default function QuestionnairePage({
  role,
  profile,
  defaultName,
  isSaving,
  error,
  onSave,
  onSkip,
  onBack,
}: QuestionnairePageProps) {
  const [displayName, setDisplayName] = useState(profile?.display_name || defaultName);
  const [phone, setPhone] = useState(profile?.phone || "");
  const [state, setState] = useState(profile?.state || "");
  const [district, setDistrict] = useState(profile?.district_name || "");
  const [farmSize, setFarmSize] = useState(
    profile?.farm_size_acres == null ? "" : String(profile.farm_size_acres),
  );
  const [ownership, setOwnership] = useState(profile?.land_ownership || "");
  const [crops, setCrops] = useState<string[]>(profile?.crops || []);
  const [interests, setInterests] = useState<string[]>(profile?.buyer_interests || []);
  const [coordinates, setCoordinates] = useState<{ lat: number; lng: number; accuracy: number } | null>(
    profile?.lat != null && profile.lng != null
      ? { lat: profile.lat, lng: profile.lng, accuracy: 0 }
      : null,
  );
  const [clearLocation, setClearLocation] = useState(false);
  const [locationMessage, setLocationMessage] = useState("");
  const [locationBusy, setLocationBusy] = useState(false);
  const [gpsError, setGpsError] = useState<string | null>(null);

  function toggleChoice(value: string, selected: string[], setSelected: (items: string[]) => void) {
    setSelected(selected.includes(value)
      ? selected.filter(item => item !== value)
      : [...selected, value]);
  }

  function requestLocation() {
    if (!navigator.geolocation) {
      setGpsError("This browser does not support location access.");
      return;
    }

    setGpsError(null);
    setLocationMessage("");
    setLocationBusy(true);
    navigator.geolocation.getCurrentPosition(
      position => {
        setCoordinates({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
          accuracy: position.coords.accuracy,
        });
        setClearLocation(false);
        setLocationMessage("Location captured. It will only be saved when you submit this form.");
        setLocationBusy(false);
      },
      locationError => {
        const messages: Record<number, string> = {
          1: "Location permission was denied. You can still save or skip the questionnaire.",
          2: "Your device could not determine a location. Try again or continue without it.",
          3: "Location lookup timed out. Try again or continue without it.",
        };
        setGpsError(messages[locationError.code] || "Could not retrieve your location.");
        setLocationBusy(false);
      },
      { enableHighAccuracy: true, timeout: 15_000, maximumAge: 0 },
    );
  }

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void onSave({
      display_name: displayName.trim(),
      phone: phone.trim(),
      state: state.trim(),
      district_name: district.trim(),
      farm_size_acres: role === "farmer" && farmSize ? Number(farmSize) : null,
      land_ownership: role === "farmer" ? ownership : "",
      crops: role === "farmer" ? crops : [],
      buyer_interests: role === "buyer" ? interests : [],
      lat: clearLocation ? null : coordinates?.lat ?? null,
      lng: clearLocation ? null : coordinates?.lng ?? null,
      clear_location: clearLocation,
    });
  }

  const choices = role === "farmer" ? cropOptions : buyerOptions;
  const selectedChoices = role === "farmer" ? crops : interests;
  const setSelectedChoices = role === "farmer" ? setCrops : setInterests;

  return (
    <main className="questionnaire-page">
      <form className="questionnaire-card" onSubmit={submit}>
        <button type="button" className="questionnaire-back" onClick={onBack}>
          <ArrowLeft size={16} /> Back
        </button>
        <div className="questionnaire-brand">
          <span className="questionnaire-brand-icon">
            {role === "farmer" ? <Sprout size={22} /> : <Store size={22} />}
          </span>
          <span><strong>KisanSetu</strong><small>Personalize your workspace</small></span>
        </div>

        <section className="questionnaire-content">
          <span className="questionnaire-eyebrow">OPTIONAL PROFILE QUESTIONNAIRE</span>
          <h1>Let’s make this useful for you</h1>
          <p>Your answers are saved to your account and can help personalize future features. You can skip now and update these details later.</p>

          {error && <div className="questionnaire-error" role="alert">{error}</div>}

          <div className="questionnaire-fields">
            <label>
              Name to show in KisanSetu
              <input maxLength={120} value={displayName} onChange={event => setDisplayName(event.target.value)} placeholder="Your preferred name" />
            </label>
            <label>
              Phone number <span className="questionnaire-optional">Optional</span>
              <input type="tel" maxLength={32} value={phone} onChange={event => setPhone(event.target.value)} placeholder="For future account features" />
            </label>
            <div className="questionnaire-field-pair">
              <label>State<input maxLength={120} value={state} onChange={event => setState(event.target.value)} placeholder="State" /></label>
              <label>District<input maxLength={120} value={district} onChange={event => setDistrict(event.target.value)} placeholder="District" /></label>
            </div>

            {role === "farmer" ? (
              <>
                <label>
                  Cultivated land (acres) <span className="questionnaire-optional">Optional</span>
                  <input type="number" min="0" max="1000000" step="0.01" value={farmSize} onChange={event => setFarmSize(event.target.value)} placeholder="e.g. 2.5" />
                </label>
                <label>
                  Land arrangement <span className="questionnaire-optional">Optional</span>
                  <select value={ownership} onChange={event => setOwnership(event.target.value)}>
                    <option value="">Choose if you want</option>
                    <option value="Owner">Owner</option>
                    <option value="Tenant">Tenant</option>
                    <option value="Sharecropper">Sharecropper</option>
                    <option value="Other">Other</option>
                  </select>
                </label>
                <fieldset className="questionnaire-choice-group">
                  <legend>Main crops <span className="questionnaire-optional">Select any</span></legend>
                  <div className="questionnaire-chips">
                    {choices.map(choice => (
                      <button
                        type="button"
                        key={choice}
                        className={selectedChoices.includes(choice) ? "questionnaire-chip selected" : "questionnaire-chip"}
                        aria-pressed={selectedChoices.includes(choice)}
                        onClick={() => toggleChoice(choice, selectedChoices, setSelectedChoices)}
                      >
                        {choice}
                      </button>
                    ))}
                  </div>
                </fieldset>
              </>
            ) : (
              <fieldset className="questionnaire-choice-group">
                <legend>Commodities of interest <span className="questionnaire-optional">Select any</span></legend>
                <div className="questionnaire-chips">
                  {choices.map(choice => (
                    <button
                      type="button"
                      key={choice}
                      className={selectedChoices.includes(choice) ? "questionnaire-chip selected" : "questionnaire-chip"}
                      aria-pressed={selectedChoices.includes(choice)}
                      onClick={() => toggleChoice(choice, selectedChoices, setSelectedChoices)}
                    >
                      {choice}
                    </button>
                  ))}
                </div>
              </fieldset>
            )}

            <section className="questionnaire-location">
              <div className="questionnaire-location-heading">
                <span className="questionnaire-location-icon"><MapPin size={18} /></span>
                <div><strong>Precise location</strong><small>Optional · stored only after you grant permission</small></div>
              </div>
              <p>Coordinates can help with location-based features. Device accuracy varies; location is never required. A deployed site must use HTTPS for browser location access.</p>
              {coordinates && !clearLocation && (
                <div className="questionnaire-coordinates">
                  <span>{coordinates.lat.toFixed(6)}, {coordinates.lng.toFixed(6)}</span>
                  {coordinates.accuracy > 0 && <small>Device accuracy about {Math.round(coordinates.accuracy)} m</small>}
                </div>
              )}
              {locationMessage && <p className="questionnaire-location-message" role="status">{locationMessage}</p>}
              {gpsError && <p className="questionnaire-location-error" role="alert">{gpsError}</p>}
              <div className="questionnaire-location-actions">
                <button type="button" className="questionnaire-location-button" onClick={requestLocation} disabled={locationBusy || isSaving}>
                  {locationBusy ? <LoaderCircle className="questionnaire-spinner" size={16} /> : <Crosshair size={16} />}
                  {coordinates && !clearLocation ? "Refresh location" : "Use my current location"}
                </button>
                {profile?.lat != null && profile.lng != null && (
                  <button type="button" className="questionnaire-remove-location" onClick={() => { setClearLocation(true); setCoordinates(null); setLocationMessage("Saved coordinates will be removed when you save."); }}>
                    Remove saved coordinates
                  </button>
                )}
              </div>
            </section>
          </div>

          <div className="questionnaire-actions">
            <button className="questionnaire-save" type="submit" disabled={isSaving}>
              {isSaving && <LoaderCircle className="questionnaire-spinner" size={17} />}
              Save and continue
            </button>
            <button className="questionnaire-skip" type="button" onClick={() => void onSkip()} disabled={isSaving}>
              Skip for now
            </button>
          </div>
          <p className="questionnaire-privacy">Location is requested only when you press the location button. Your browser may show a permission prompt.</p>
        </section>
      </form>
    </main>
  );
}
