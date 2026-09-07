import { useState } from 'react'
import './App.css'

// Base URL of the Flask backend. Hardcoded because this app only ever runs
// locally against `flask run` on its default address (per the handover doc,
// there's no deployment story and no need for env-based config here).
const API_BASE_URL = 'http://127.0.0.1:5000'

// The backend has exactly one route: GET /<setName>/<cardName>, where both
// segments are raw path pieces (not query params). It always responds with
// either 200 + { imageUrl, price } or a non-200 (usually 404) + an error
// body. Every non-200 case (unknown set/card, DB error, etc.) means the
// same thing to the frontend: "no match" — the backend doesn't distinguish
// them, so we don't try to either.
//
// `status` tracks where we are in that single request/response cycle:
//   'idle'    - nothing submitted yet
//   'loading' - request in flight (show the animated dots)
//   'success' - got a 200, `result` holds { imageUrl, price }
//   'error'   - anything else (bad response or network failure)
function App() {
  const [setName, setSetName] = useState('')
  const [cardName, setCardName] = useState('')
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)

  async function handleSubmit(event) {
    // Stop the browser from doing a full page reload on form submit.
    event.preventDefault()

    setStatus('loading')
    setResult(null)

    // Both inputs are free text (set names contain spaces/punctuation, e.g.
    // "ME05: Pitch Black"), so each one must be URL-encoded before being
    // dropped into the path — otherwise those characters would break the
    // request URL or get parsed as extra path segments.
    const url = `${API_BASE_URL}/${encodeURIComponent(setName)}/${encodeURIComponent(cardName)}`

    try {
      const response = await fetch(url)

      if (!response.ok) {
        // Covers the documented 404 "not found" as well as any other
        // non-200 status — treated identically per the API contract.
        setStatus('error')
        return
      }

      const data = await response.json()
      setResult(data)
      setStatus('success')
    } catch {
      // Network failure (backend not running, DNS error, etc.) is
      // indistinguishable from "no match" as far as the user is concerned.
      setStatus('error')
    }
  }

  // Require both fields to have real (non-whitespace-only) content before
  // a lookup can be submitted — avoids firing pointless requests for blank
  // path segments.
  const canSubmit = setName.trim() !== '' && cardName.trim() !== ''

  return (
    <div className="page">
      <h1>Pokemon Card Price Lookup</h1>

      <form onSubmit={handleSubmit} className="lookup-form">
        <label>
          Set name
          <input
            type="text"
            value={setName}
            onChange={(e) => setSetName(e.target.value)}
            placeholder="e.g. ME05: Pitch Black"
          />
        </label>

        <label>
          Card name
          <input
            type="text"
            value={cardName}
            onChange={(e) => setCardName(e.target.value)}
            placeholder="e.g. Mega Darkrai ex - 116/084"
          />
        </label>

        <button type="submit" disabled={!canSubmit || status === 'loading'}>
          Look up
        </button>
      </form>

      <div className="result-area">
        {status === 'loading' && <LoadingDots />}

        {status === 'error' && <p className="no-match">No match found.</p>}

        {status === 'success' && result && (
          <div className="card-result">
            <img
              src={result.imageUrl}
              alt={`${cardName} (${setName})`}
              className="card-image"
            />
            {/* price can legitimately be null if sync.py never found a
                market price for this card — show a fallback instead of
                the literal "null"/"undefined". */}
            <p className="card-price">
              {result.price != null ? `$${result.price}` : 'Price unavailable'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

// Three dots that pulse in sequence via CSS animation (see .dots span
// rules in App.css). Purely visual — no timers/state needed, CSS keyframes
// with staggered animation-delay do the "moving dots" effect on their own.
function LoadingDots() {
  return (
    <div className="dots" role="status" aria-label="Loading">
      <span></span>
      <span></span>
      <span></span>
    </div>
  )
}

export default App
