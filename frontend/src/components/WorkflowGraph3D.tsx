import { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Text, Sphere, Line } from '@react-three/drei'
import * as THREE from 'three'

interface WorkflowNode {
  id: string
  label: string
  position: [number, number, number]
  color: string
}

interface WorkflowGraph3DProps {
  currentStep: string | null
}

function Node({ node, isActive }: { node: WorkflowNode; isActive: boolean }) {
  const meshRef = useRef<THREE.Mesh>(null)
  
  useFrame((state) => {
    if (meshRef.current && isActive) {
      meshRef.current.rotation.y += 0.02
      meshRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 3) * 0.1)
    }
  })

  return (
    <group position={node.position}>
      <Sphere ref={meshRef} args={[0.3, 32, 32]}>
        <meshStandardMaterial
          color={isActive ? '#10b981' : node.color}
          emissive={isActive ? '#10b981' : '#000000'}
          emissiveIntensity={isActive ? 0.5 : 0}
        />
      </Sphere>
      <Text
        position={[0, -0.6, 0]}
        fontSize={0.15}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {node.label}
      </Text>
    </group>
  )
}

function ConnectionLine({ start, end }: { start: [number, number, number]; end: [number, number, number] }) {
  const points = useMemo(() => [
    new THREE.Vector3(...start),
    new THREE.Vector3(...end)
  ], [start, end])

  return (
    <Line
      points={points}
      color="#4b5563"
      lineWidth={2}
      dashed={false}
    />
  )
}

export default function WorkflowGraph3D({ currentStep }: WorkflowGraph3DProps) {
  const nodes: WorkflowNode[] = [
    { id: 'detect', label: '🔍 Detect', position: [0, 2, 0], color: '#3b82f6' },
    { id: 'analyze', label: '📊 Analyze', position: [-2, 1, 0], color: '#8b5cf6' },
    { id: 'generate', label: '🤖 Generate', position: [-2, 0, 0], color: '#ec4899' },
    { id: 'approve', label: '✋ Approve', position: [0, -1, 0], color: '#f59e0b' },
    { id: 'commit', label: '💾 Commit', position: [2, 0, 0], color: '#10b981' },
    { id: 'push_approve', label: '✋ Push?', position: [2, 1, 0], color: '#f59e0b' },
    { id: 'push', label: '🚀 Push', position: [0, 2, 0], color: '#06b6d4' },
  ]

  const connections = [
    { start: nodes[0].position, end: nodes[1].position },
    { start: nodes[1].position, end: nodes[2].position },
    { start: nodes[2].position, end: nodes[3].position },
    { start: nodes[3].position, end: nodes[4].position },
    { start: nodes[4].position, end: nodes[5].position },
    { start: nodes[5].position, end: nodes[6].position },
  ]

  return (
    <div className="w-full h-full">
      <Canvas camera={{ position: [0, 0, 8], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <pointLight position={[-10, -10, -10]} intensity={0.5} />
        
        {connections.map((conn, i) => (
          <ConnectionLine key={i} start={conn.start} end={conn.end} />
        ))}
        
        {nodes.map((node) => (
          <Node
            key={node.id}
            node={node}
            isActive={currentStep === node.id}
          />
        ))}
        
        <OrbitControls enableZoom={true} enablePan={false} />
      </Canvas>
    </div>
  )
}
