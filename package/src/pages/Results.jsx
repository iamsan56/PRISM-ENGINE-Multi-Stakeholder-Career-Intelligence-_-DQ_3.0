export default function Results() {
  return (
    <div className="results-page">

      <div className="results-container">

        <p className="eyebrow">
          PRISM ANALYSIS
        </p>

        <h1>Your Career Recommendations</h1>

        <div className="career-card">
          <h2>VLSI Engineer</h2>

          <p>Career Fit: 91%</p>
          <p>Affordability: 84%</p>
          <p>Demand: 92%</p>
          <p>ROI: 89%</p>

          <button>
            Explore Career
          </button>
        </div>

        <div className="career-card">
          <h2>Embedded Engineer</h2>

          <p>Career Fit: 87%</p>
          <p>Affordability: 90%</p>
          <p>Demand: 88%</p>
          <p>ROI: 85%</p>

          <button>
            Explore Career
          </button>
        </div>

      </div>

    </div>
  );
}