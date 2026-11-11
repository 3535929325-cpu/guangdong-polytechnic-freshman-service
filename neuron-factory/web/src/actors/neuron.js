import * as THREE from "three";

function makeLabelTexture(text, bg = "#F5EDE0", fg = "#3A2A30") {
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 160;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = "#e0d2c4";
  ctx.lineWidth = 10;
  ctx.strokeRect(8, 8, canvas.width - 16, canvas.height - 16);
  ctx.fillStyle = fg;
  ctx.font = "700 52px 'Noto Sans SC', 'Zen Maru Gothic', sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(text, canvas.width / 2, canvas.height / 2);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

export function createNeuronAgent({ label, color, hero = false, palette }) {
  const root = new THREE.Group();
  root.name = label;
  const scale = hero ? 1.15 : 0.72;

  const bodyMat = new THREE.MeshStandardMaterial({
    color,
    roughness: 0.48,
    metalness: 0.02,
  });
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.55 * scale, 32, 24), bodyMat);
  body.position.y = 0.7 * scale;
  body.castShadow = true;
  root.add(body);

  const eyeWhite = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.3 });
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x1a1218, roughness: 0.2 });
  [-0.18, 0.18].forEach((x) => {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.12 * scale, 16, 12), eyeWhite);
    eye.position.set(x * scale, 0.85 * scale, 0.42 * scale);
    root.add(eye);
    const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.05 * scale, 12, 10), pupilMat);
    pupil.position.set(x * scale, 0.85 * scale, 0.52 * scale);
    root.add(pupil);
  });

  // mouth
  const mouth = new THREE.Mesh(
    new THREE.TorusGeometry(0.06 * scale, 0.012 * scale, 8, 16, Math.PI),
    new THREE.MeshStandardMaterial({ color: 0x5a3040 })
  );
  mouth.position.set(0, 0.62 * scale, 0.5 * scale);
  mouth.rotation.x = Math.PI;
  root.add(mouth);

  for (let i = 0; i < 8; i++) {
    const ang = (i / 8) * Math.PI * 2;
    const dend = new THREE.Mesh(
      new THREE.CapsuleGeometry(0.035 * scale, 0.55 * scale, 4, 8),
      bodyMat
    );
    dend.position.set(
      Math.cos(ang) * 0.55 * scale,
      1.15 * scale + Math.sin(ang * 2) * 0.08,
      Math.sin(ang) * 0.35 * scale
    );
    dend.rotation.z = Math.cos(ang) * 0.5;
    dend.rotation.x = Math.sin(ang) * 0.4;
    root.add(dend);
  }

  const plate = new THREE.Mesh(
    new THREE.PlaneGeometry(0.85 * scale, 0.28 * scale),
    new THREE.MeshStandardMaterial({
      map: makeLabelTexture(label, palette.cream),
      roughness: 0.5,
    })
  );
  plate.position.set(0, 0.55 * scale, 0.56 * scale);
  root.add(plate);

  root.userData = { label, hero, bodyMat, baseScale: scale };
  return root;
}

export function createWordBox(label, palette) {
  const root = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({
    color: palette.cream,
    roughness: 0.65,
  });
  const box = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.38, 0.58), mat);
  box.castShadow = true;
  root.add(box);

  const face = new THREE.Mesh(
    new THREE.PlaneGeometry(0.82, 0.3),
    new THREE.MeshStandardMaterial({
      map: makeLabelTexture(label),
      roughness: 0.45,
    })
  );
  face.position.set(0, 0.02, 0.3);
  root.add(face);
  root.userData.label = label;
  return root;
}
