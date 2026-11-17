import { Canvas, useFrame } from "@react-three/fiber";
import { Float, OrbitControls, Stars } from "@react-three/drei";
import { useRef } from "react";

function DataCube() {
  const cube = useRef();

  useFrame((state, delta) => {
    if (!cube.current) return;

    cube.current.rotation.x += delta * 0.35;
    cube.current.rotation.y += delta * 0.55;
  });

  return (
    <Float
      speed={2}
      rotationIntensity={0.6}
      floatIntensity={1.2}
    >
      <mesh ref={cube}>
        <boxGeometry args={[1.8, 1.8, 1.8]} />

        <meshStandardMaterial
          color="#3b82f6"
          metalness={0.8}
          roughness={0.18}
          transparent
          opacity={0.85}
        />
      </mesh>

      <mesh scale={1.35}>
        <boxGeometry args={[1.8, 1.8, 1.8]} />

        <meshBasicMaterial
          color="#8b5cf6"
          wireframe
          transparent
          opacity={0.45}
        />
      </mesh>
    </Float>
  );
}

function ThreeDScene() {
  return (
    <div className="three-scene">
      <Canvas camera={{ position: [0, 0, 5], fov: 50 }}>
        <ambientLight intensity={1.5} />

        <directionalLight
          position={[3, 4, 5]}
          intensity={3}
          color="#60a5fa"
        />

        <pointLight
          position={[-3, -2, 2]}
          intensity={4}
          color="#8b5cf6"
        />

        <Stars
          radius={35}
          depth={20}
          count={1200}
          factor={2}
          fade
          speed={0.7}
        />

        <DataCube />

        <OrbitControls
          enableZoom={false}
          enablePan={false}
          autoRotate
          autoRotateSpeed={1.5}
        />
      </Canvas>

      <div className="three-label">
        <span>3D DATA CORE</span>
        <strong>PROCESSING ACTIVE</strong>
      </div>
    </div>
  );
}

export default ThreeDScene;