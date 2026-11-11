import * as THREE from "three";

export function createCourier(palette) {
  const root = new THREE.Group();
  root.name = "Courier";

  const bodyMat = new THREE.MeshStandardMaterial({
    color: palette.courierBlue,
    roughness: 0.42,
    metalness: 0.05,
  });
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.9, 0.28), bodyMat);
  body.position.y = 0.55;
  body.castShadow = true;
  root.add(body);

  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.15 });
  const hlMat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    emissive: 0xffffff,
    emissiveIntensity: 0.35,
  });
  [-0.18, 0.18].forEach((x) => {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.09, 16, 12), eyeMat);
    eye.position.set(x, 0.72, 0.16);
    root.add(eye);
    const hl = new THREE.Mesh(new THREE.SphereGeometry(0.025, 8, 8), hlMat);
    hl.position.set(x - 0.02, 0.75, 0.23);
    root.add(hl);
  });

  const logo = new THREE.Mesh(
    new THREE.CircleGeometry(0.2, 32),
    new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.35 })
  );
  logo.position.set(0, 0.48, 0.15);
  root.add(logo);

  const spark = new THREE.Mesh(
    new THREE.SphereGeometry(0.05, 12, 12),
    new THREE.MeshStandardMaterial({
      color: palette.amber,
      emissive: palette.amber,
      emissiveIntensity: 1.4,
    })
  );
  spark.position.set(0, 0.48, 0.17);
  root.add(spark);

  // orbital rings on logo
  const ring = new THREE.Mesh(
    new THREE.TorusGeometry(0.12, 0.012, 8, 48),
    new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.3 })
  );
  ring.position.copy(logo.position);
  ring.rotation.x = 0.9;
  ring.rotation.z = 0.5;
  root.add(ring);

  const black = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.5 });
  const white = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.4 });
  [-1, 1].forEach((side) => {
    const arm = new THREE.Mesh(new THREE.CapsuleGeometry(0.05, 0.12, 4, 8), black);
    arm.position.set(side * 0.52, 0.45, 0);
    arm.rotation.z = side * 0.4;
    root.add(arm);
    const hand = new THREE.Mesh(new THREE.CapsuleGeometry(0.1, 0.08, 4, 10), white);
    hand.position.set(side * 0.62, 0.32, 0.05);
    hand.rotation.z = Math.PI / 2;
    root.add(hand);
    const foot = new THREE.Mesh(new THREE.CapsuleGeometry(0.1, 0.16, 4, 10), white);
    foot.position.set(side * 0.2, 0.08, 0.02);
    foot.rotation.z = Math.PI / 2;
    root.add(foot);
  });

  return root;
}
