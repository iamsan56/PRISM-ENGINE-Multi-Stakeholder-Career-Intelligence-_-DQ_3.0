import * as THREE from 'three';
import { Edges } from '@react-three/drei';

const shape = new THREE.Shape();
shape.moveTo(-1.5, -1);
shape.lineTo(1.5, -1);
shape.lineTo(0, 1.5);
shape.closePath();

const extrudeSettings = {
  depth: 2,
  bevelEnabled: true,
  bevelSegments: 4,
  steps: 1,
  bevelSize: 0.05,
  bevelThickness: 0.05,
};

export default function PrismMesh() {
  return (
    <mesh rotation={[0.25, -0.55, 0.15]}>
      <extrudeGeometry args={[shape, extrudeSettings]} />
      <meshPhysicalMaterial
        color="#8b5cf6"
        roughness={0.05}
        metalness={0.05}
        transmission={0.75}
        thickness={1.8}
        ior={1.45}
        transparent
        opacity={0.85}
        emissive="#5b21b6"
        emissiveIntensity={0.3}
      />
      <Edges scale={1.02} color="#e9d5ff" />
    </mesh>
  );
}
