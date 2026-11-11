import * as THREE from "three";
import { createCourier } from "../actors/courier.js";
import { createNeuronAgent, createWordBox } from "../actors/neuron.js";
import { eventProgress, smoothstep } from "../director/timeline.js";

function hex(c) {
  return new THREE.Color(c);
}

export function createFactoryScene(story) {
  const scene = new THREE.Scene();
  scene.background = hex(story.palette.bgDeep);
  scene.fog = new THREE.Fog(0xe8d2c8, 12, 42);
  scene.background = hex("#EAD3CB");

  const root = new THREE.Group();
  scene.add(root);

  // lights
  const hemi = new THREE.HemisphereLight(0xffe8e0, 0x2a1f28, 0.85);
  scene.add(hemi);
  const key = new THREE.DirectionalLight(0xffe6dc, 1.35);
  key.position.set(6, 10, 4);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xd8e8ff, 0.55);
  fill.position.set(-8, 4, -2);
  scene.add(fill);
  const heart = new THREE.PointLight(0xffc8c0, 2.2, 18, 1.6);
  heart.position.set(0, 2.2, -1);
  scene.add(heart);

  // floor + dome feel
  const floor = new THREE.Mesh(
    new THREE.CircleGeometry(22, 64),
    new THREE.MeshStandardMaterial({ color: 0xd8b8b0, roughness: 0.92 })
  );
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  root.add(floor);

  const dome = new THREE.Mesh(
    new THREE.SphereGeometry(20, 48, 32, 0, Math.PI * 2, 0, Math.PI * 0.55),
    new THREE.MeshStandardMaterial({
      color: 0xe5c2bc,
      side: THREE.BackSide,
      roughness: 0.9,
    })
  );
  dome.position.y = 1;
  root.add(dome);

  // nerve tubes
  for (let i = 0; i < 18; i++) {
    const ang = (i / 18) * Math.PI * 2;
    const r = 7 + (i % 3) * 1.15;
    const tube = new THREE.Mesh(
      new THREE.CapsuleGeometry(0.4 + (i % 4) * 0.07, 7, 4, 10),
      new THREE.MeshStandardMaterial({
        color: i % 2 ? 0xd9c0e0 : 0xe8b8c4,
        roughness: 0.78,
      })
    );
    tube.position.set(Math.cos(ang) * r, 4.5 + (i % 5) * 0.4, Math.sin(ang) * r * 0.7 - 2);
    tube.rotation.z = Math.cos(ang) * 0.5;
    tube.rotation.x = 0.9;
    root.add(tube);
  }

  // gate
  const gate = new THREE.Mesh(
    new THREE.TorusGeometry(2.1, 0.16, 16, 64),
    new THREE.MeshStandardMaterial({
      color: 0xf0c8c0,
      emissive: 0xffd0c8,
      emissiveIntensity: 0.25,
      roughness: 0.45,
    })
  );
  gate.position.set(0, 1.6, 6.2);
  root.add(gate);

  // conveyor belt as ribbon path (parametric — avoids CatmullRom edge cases)
  function beltPoint(u, target = new THREE.Vector3()) {
    const t = ((u % 1) + 1) % 1;
    const ang = t * Math.PI * 2.4;
    const r = 3.2 - t * 1.2;
    return target.set(
      Math.cos(ang) * r,
      0.2 + Math.sin(t * Math.PI * 2) * 0.12 + t * 0.35,
      Math.sin(ang) * r * 0.55 - 0.5
    );
  }
  const beltPts = [];
  for (let i = 0; i <= 80; i++) beltPts.push(beltPoint(i / 80));
  const beltCurve = new THREE.CatmullRomCurve3(beltPts);
  beltCurve.curveType = "centripetal";
  const beltGeo = new THREE.TubeGeometry(beltCurve, 200, 0.22, 12, false);
  const belt = new THREE.Mesh(
    beltGeo,
    new THREE.MeshStandardMaterial({ color: story.palette.flesh, roughness: 0.72 })
  );
  root.add(belt);

  // segmented pads on belt for visual rhythm
  const padPos = new THREE.Vector3();
  for (let i = 0; i < 36; i++) {
    beltPoint(i / 36, padPos);
    const pad = new THREE.Mesh(
      new THREE.BoxGeometry(0.55, 0.06, 0.4),
      new THREE.MeshStandardMaterial({ color: 0xe0b0a4, roughness: 0.7 })
    );
    pad.position.copy(padPos);
    pad.position.y += 0.12;
    root.add(pad);
  }

  const courier = createCourier(story.palette);
  root.add(courier);

  const labels = [story.words.form, ...story.words.background];
  const boxes = labels.map((label, i) => {
    const box = createWordBox(label, story.palette);
    box.userData.index = i;
    root.add(box);
    return box;
  });

  const agentForm = createNeuronAgent({
    label: story.words.form,
    color: story.palette.neuronPink,
    hero: true,
    palette: story.palette,
  });
  agentForm.position.set(1.35, 0, -0.6);
  agentForm.rotation.y = -0.35;
  root.add(agentForm);

  const agentMeaning = createNeuronAgent({
    label: story.words.meaning,
    color: story.palette.neuronBlue,
    hero: true,
    palette: story.palette,
  });
  agentMeaning.position.set(-1.35, 0, -0.6);
  agentMeaning.rotation.y = 0.35;
  root.add(agentMeaning);

  // crowd: ringed around a clear stage (no ball-pit in the hero zone)
  const crowdGeo = new THREE.SphereGeometry(0.38, 16, 12);
  const crowdMat = new THREE.MeshStandardMaterial({ roughness: 0.55 });
  const crowdCount = 140;
  const crowd = new THREE.InstancedMesh(crowdGeo, crowdMat, crowdCount);
  crowd.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  const dummy = new THREE.Object3D();
  const color = new THREE.Color();
  const crowdMeta = [];
  let placed = 0;
  for (let i = 0; placed < crowdCount && i < 400; i++) {
    const ang = (i / 400) * Math.PI * 2 + (i % 3) * 0.15;
    const r = 5.2 + (i % 9) * 0.55 + (i % 5) * 0.12;
    const x = Math.cos(ang) * r;
    const z = Math.sin(ang) * r * 0.72 - 1.8;
    // keep center stage clear for heroes / conveyor
    if (Math.hypot(x, z + 0.6) < 3.6) continue;
    dummy.position.set(x, 0.42, z);
    dummy.scale.setScalar(0.65 + (placed % 5) * 0.07);
    dummy.updateMatrix();
    crowd.setMatrixAt(placed, dummy.matrix);
    color.set(placed % 2 ? story.palette.neuronPink : story.palette.neuronBlue);
    crowd.setColorAt(placed, color);
    crowdMeta.push({ x, z, baseY: 0.42 });
    placed++;
  }
  crowd.count = placed;
  crowd.castShadow = true;
  root.add(crowd);

  // dendrite arm
  const arm = new THREE.Group();
  arm.name = "DendriteArm";
  const armMat = new THREE.MeshStandardMaterial({
    color: story.palette.neuronPink,
    roughness: 0.5,
  });
  for (let i = 0; i < 5; i++) {
    const seg = new THREE.Mesh(new THREE.CapsuleGeometry(0.08 - i * 0.008, 0.55, 4, 8), armMat);
    seg.position.set(0.05 * i, -0.55 * i, 0.08 * i);
    arm.add(seg);
  }
  const claw = new THREE.Mesh(new THREE.SphereGeometry(0.14, 12, 10), armMat);
  claw.position.set(0.25, -2.6, 0.35);
  arm.add(claw);
  arm.position.set(0.4, 4.0, 0.2);
  root.add(arm);

  // synapses
  const synGroup = new THREE.Group();
  const synMatA = new THREE.MeshStandardMaterial({
    color: story.palette.neuronPink,
    emissive: story.palette.neuronPink,
    emissiveIntensity: 0.5,
    roughness: 0.35,
  });
  const synMatB = new THREE.MeshStandardMaterial({
    color: story.palette.amber,
    emissive: story.palette.amber,
    emissiveIntensity: 0.5,
    roughness: 0.35,
  });
  const synA = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 1, 10), synMatA);
  const synB = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 1, 10), synMatB);
  synA.visible = false;
  synB.visible = false;
  synGroup.add(synA, synB);

  const handMat = new THREE.MeshStandardMaterial({
    color: story.palette.warmWhite,
    emissive: story.palette.warmWhite,
    emissiveIntensity: 0.2,
  });
  const handA = new THREE.Mesh(new THREE.CapsuleGeometry(0.1, 0.1, 4, 10), handMat);
  const handB = new THREE.Mesh(new THREE.CapsuleGeometry(0.1, 0.1, 4, 10), handMat.clone());
  handA.visible = false;
  handB.visible = false;
  synGroup.add(handA, handB);
  root.add(synGroup);

  const flash = new THREE.PointLight(0xfff6e8, 0, 12, 2);
  flash.position.set(0, 1.6, -0.8);
  scene.add(flash);

  const state = {
    scene,
    courier,
    boxes,
    agentForm,
    agentMeaning,
    crowd,
    crowdMeta,
    arm,
    claw,
    synA,
    synB,
    handA,
    handB,
    heart,
    flash,
    beltPoint,
    dummy,
    color,
  };

  const tmpBox = new THREE.Vector3();
  function placeBox(box, t, i) {
    const speed = 0.12;
    const u = (i / boxes.length + t * speed) % 1;
    beltPoint(u, tmpBox);
    box.position.copy(tmpBox);
    box.position.y += 0.28;
    box.rotation.y = t * 0.2 + i;
    // lock form box during assign
    if (i === 0 && t >= 26) {
      const grab = smoothstep((t - 26) / 4);
      box.position.lerp(new THREE.Vector3(1.35, 1.15, -0.35), grab);
    }
    if (i === 0 && t >= 30.5) {
      box.position.lerp(new THREE.Vector3(1.45, 1.25, -0.35), smoothstep((t - 30.5) / 2));
      box.visible = t < 33;
    }
  }

  function updateArm(t) {
    if (t < 24) {
      arm.position.set(0.4, 4.2, 0.2);
      return;
    }
    if (t < 35) {
      const u = smoothstep((t - 25) / 8);
      arm.position.set(0.6 + u * 0.7, 4.0 - u * 2.2, 0.2 - u * 0.4);
      arm.rotation.z = -u * 0.6;
      arm.rotation.x = u * 0.3;
      return;
    }
    if (t < 42) {
      arm.position.set(0.8, 2.6, -0.1);
      return;
    }
    if (t < 52) {
      const u = smoothstep((t - 43) / 7);
      arm.position.set(0.2 - u * 1.5, 3.8 - u * 2.0, 0.1 - u * 0.6);
      arm.rotation.z = u * 0.55;
      return;
    }
    arm.position.set(-0.8, 2.5, -0.4);
  }

  function updateSynapse(t) {
    const grow = eventProgress(story, "synapseGrow", t);
    const handshake = eventProgress(story, "handshake", t);
    const remembered = eventProgress(story, "rememberFlash", t);
    if (grow <= 0) {
      synA.visible = synB.visible = handA.visible = handB.visible = false;
      flash.intensity = 0;
      return;
    }
    synA.visible = synB.visible = true;
    handA.visible = handB.visible = true;

    const a = agentForm.position.clone().add(new THREE.Vector3(-0.15, 0.95, 0.35));
    const b = agentMeaning.position.clone().add(new THREE.Vector3(0.15, 0.95, 0.35));
    const mid = new THREE.Vector3(0, 1.35, -0.35);
    const aEnd = a.clone().lerp(mid, grow);
    const bEnd = b.clone().lerp(mid, grow);

    const align = (mesh, from, to) => {
      const dir = new THREE.Vector3().subVectors(to, from);
      const len = Math.max(0.01, dir.length());
      mesh.position.copy(from).add(to).multiplyScalar(0.5);
      mesh.scale.set(1, len, 1);
      mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.clone().normalize());
    };
    align(synA, a, aEnd);
    align(synB, b, bEnd);

    handA.position.copy(aEnd);
    handB.position.copy(bEnd);
    handA.rotation.z = Math.PI / 2;
    handB.rotation.z = Math.PI / 2;

    if (handshake) {
      handA.position.lerp(mid.clone().add(new THREE.Vector3(-0.1, 0, 0)), handshake);
      handB.position.lerp(mid.clone().add(new THREE.Vector3(0.1, 0, 0)), handshake);
    }
    if (remembered) {
      const pulse = 0.5 + Math.sin(t * 10) * 0.5;
      flash.intensity = 10 * remembered * (0.7 + 0.3 * pulse);
      handA.scale.setScalar(1.1 + remembered * 0.7);
      handB.scale.setScalar(1.1 + remembered * 0.7);
      heart.intensity = 2.2 + remembered * 5;
      synMatA.emissiveIntensity = 0.5 + remembered * 1.4;
      synMatB.emissiveIntensity = 0.5 + remembered * 1.4;
      agentForm.scale.setScalar(1 + remembered * 0.08);
      agentMeaning.scale.setScalar(1 + remembered * 0.08);
    } else {
      flash.intensity = grow * 1.4;
      heart.intensity = 2.2;
    }
  }

  function updateCrowd(t) {
    const lift = eventProgress(story, "liftSea", t);
    for (let i = 0; i < crowdMeta.length; i++) {
      const m = crowdMeta[i];
      const bob = Math.sin(t * 1.5 + i) * 0.05;
      dummy.position.set(m.x, m.baseY + bob + lift * (0.4 + (i % 9) * 0.03), m.z);
      const highlight =
        (Math.hypot(m.x - 1.45, m.z + 0.5) < 1.2 || Math.hypot(m.x + 1.55, m.z + 1.0) < 1.2) &&
        t >= 35;
      dummy.scale.setScalar((0.7 + (i % 5) * 0.08) * (highlight ? 1.25 : 1));
      dummy.updateMatrix();
      crowd.setMatrixAt(i, dummy.matrix);
      color.set(i % 2 ? story.palette.neuronPink : story.palette.neuronBlue);
      if (highlight) color.offsetHSL(0, 0.1, 0.12);
      else if (t >= 35) color.multiplyScalar(0.55);
      crowd.setColorAt(i, color);
    }
    crowd.instanceMatrix.needsUpdate = true;
    if (crowd.instanceColor) crowd.instanceColor.needsUpdate = true;
  }

  function updateAgents(t) {
    const assignForm = eventProgress(story, "assignAgent", t) && t >= 30 && t < 42;
    // scale punch around assign times
    const formPulse = t >= 30.5 && t < 33 ? 1 + Math.sin((t - 30.5) * 8) * 0.06 : 1;
    const meanPulse = t >= 48.5 && t < 51 ? 1 + Math.sin((t - 48.5) * 8) * 0.06 : 1;
    agentForm.scale.setScalar(formPulse);
    agentMeaning.scale.setScalar(meanPulse);
    agentForm.rotation.y = Math.sin(t * 0.6) * 0.08;
    agentMeaning.rotation.y = Math.sin(t * 0.55 + 1) * 0.08;
    if (assignForm) {
      agentForm.position.y = 0.05;
    }
  }

  const tmpCourier = new THREE.Vector3();
  function updateCourier(t) {
    // start near gate on the outer belt, ride inward
    const u = Math.min(1, t / 12);
    beltPoint(0.78 - u * 0.35, tmpCourier);
    courier.position.copy(tmpCourier);
    courier.position.y += 0.42;
    courier.rotation.y = Math.PI + Math.sin(t) * 0.05;
    courier.position.y += Math.sin(t * 3) * 0.02;
    if (t > 18) {
      courier.position.lerp(new THREE.Vector3(0.15, 0.55, 1.6), smoothstep((t - 18) / 10));
      courier.rotation.y = Math.PI * 0.15;
    }
    // keep courier readable during assign / climax as observer
    if (t > 28) {
      courier.position.lerp(new THREE.Vector3(0.2, 0.55, 1.35), 0.2);
    }
  }

  function update(t) {
    updateCourier(t);
    boxes.forEach((box, i) => placeBox(box, t, i));
    updateArm(t);
    updateAgents(t);
    updateCrowd(t);
    updateSynapse(t);
  }

  return { scene, update, state };
}
