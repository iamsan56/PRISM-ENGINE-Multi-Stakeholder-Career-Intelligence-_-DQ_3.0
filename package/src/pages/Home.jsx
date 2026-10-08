import { Canvas } from "@react-three/fiber";
import {
  OrbitControls,
  Stars,
  Environment,
  ContactShadows,
} from "@react-three/drei";

import Prism from "../Prism";

export default function Home() {
  return (
    <div className="app">

      <div className="hero-text">
        <div className="eyebrow">
          AI CAREER GUIDANCE
        </div>

        <h1>PRISM</h1>

        <p>
          Find the career that fits you.
        </p>

        <button
          className="start-button"
          onClick={() => {
            window.location.href = "/assessment";
          }}
        >
          START YOUR JOURNEY
        </button>
      </div>

      <Canvas
        shadows
        camera={{
          position: [0, 0, 7],
          fov: 45,
        }}
      >

        <ambientLight intensity={0.7} />

        <directionalLight
          position={[4, 5, 6]}
          intensity={3.5}
          castShadow
        />

        <pointLight
          position={[-4, 2, 3]}
          intensity={5}
          color="#a855f7"
        />

        <pointLight
          position={[4, -1, 3]}
          intensity={4}
          color="#2563eb"
        />

        <pointLight
          position={[1, 4, -2]}
          intensity={3}
          color="#ec4899"
        />

        <Stars
          radius={100}
          depth={50}
          count={2500}
          factor={3}
          saturation={0}
          fade
          speed={0.4}
        />

        <Environment preset="night" />

        <Prism />

        <ContactShadows
          position={[1.8, -1.1, 0]}
          opacity={0.5}
          scale={5}
          blur={2.5}
          far={4}
        />

        <OrbitControls
          enablePan={false}
          enableZoom={true}
          enableDamping
          dampingFactor={0.08}
        />

      </Canvas>

    </div>
  );
}