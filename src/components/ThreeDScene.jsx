import { Canvas } from "@react-three/fiber";
import { Float, OrbitControls } from "@react-three/drei";

function ThreeDScene() {
  return (
    <div
      style={{
        height: 260,
        borderRadius: 16,
        overflow: "hidden",
        marginBottom: 24,
        background: "linear-gradient(135deg, #0f172a, #1e3a8a)",
      }}
    >
      <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
        <ambientLight intensity={0.9} />
        <directionalLight position={[3, 4, 2]} intensity={1.2} />
        <Float speed={2.5} rotationIntensity={0.4} floatIntensity={0.6}>
          <mesh>
            <boxGeometry args={[1.6, 1.6, 1.6]} />
            <meshStandardMaterial color="#4f8cff" emissive="#17315f" />
          </mesh>
        </Float>
        <OrbitControls enableZoom={false} autoRotate />
      </Canvas>
    </div>
  );
}

export default ThreeDScene;
