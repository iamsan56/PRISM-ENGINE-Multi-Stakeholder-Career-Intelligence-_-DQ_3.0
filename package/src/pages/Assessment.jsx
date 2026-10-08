import { useState } from "react";

export default function Assessment() {
  const [student, setStudent] = useState({
    name: "",
    riasec: "",
    aptitude: "",
    interest: "",
  });

  const [parent, setParent] = useState({
    budget: "",
    location: "",
    preference: "",
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    const data = {
      student,
      parent,
    };

    console.log("PRISM INPUT:", data);

    window.location.href = "/results";
  };

  return (
    <div className="assessment-page">

      <div className="assessment-container">

        <h1>PRISM Assessment</h1>

        <p>
          Tell us about yourself so PRISM can find suitable career paths.
        </p>

        <form onSubmit={handleSubmit}>

          <h2>Student Profile</h2>

          <input
            type="text"
            placeholder="Your name"
            value={student.name}
            onChange={(e) =>
              setStudent({
                ...student,
                name: e.target.value,
              })
            }
          />

          <input
            type="text"
            placeholder="RIASEC profile"
            value={student.riasec}
            onChange={(e) =>
              setStudent({
                ...student,
                riasec: e.target.value,
              })
            }
          />

          <input
            type="text"
            placeholder="Aptitude"
            value={student.aptitude}
            onChange={(e) =>
              setStudent({
                ...student,
                aptitude: e.target.value,
              })
            }
          />

          <input
            type="text"
            placeholder="Interests"
            value={student.interest}
            onChange={(e) =>
              setStudent({
                ...student,
                interest: e.target.value,
              })
            }
          />

          <h2>Parent Profile</h2>

          <input
            type="number"
            placeholder="Education budget (₹)"
            value={parent.budget}
            onChange={(e) =>
              setParent({
                ...parent,
                budget: e.target.value,
              })
            }
          />

          <input
            type="text"
            placeholder="Preferred location"
            value={parent.location}
            onChange={(e) =>
              setParent({
                ...parent,
                location: e.target.value,
              })
            }
          />

          <input
            type="text"
            placeholder="Parent preference"
            value={parent.preference}
            onChange={(e) =>
              setParent({
                ...parent,
                preference: e.target.value,
              })
            }
          />

          <button type="submit">
            ANALYZE MY CAREER
          </button>

        </form>

      </div>

    </div>
  );
}