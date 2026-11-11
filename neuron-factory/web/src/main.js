import * as THREE from "three";
import story from "../../shared/storyboard.json";
import {
  DirectorClock,
  cameraPose,
  shotAt,
  subtitleAt,
} from "./director/timeline.js";
import { createFactoryScene } from "./scenes/factory.js";

const app = document.getElementById("app");
const playBtn = document.getElementById("playBtn");
const restartBtn = document.getElementById("restartBtn");
const timeLabel = document.getElementById("timeLabel");
const subtitleEl = document.getElementById("subtitle");
const seek = document.getElementById("seek");
const shotTag = document.getElementById("shotTag");
const hud = document.getElementById("hud");
const captureMode = new URLSearchParams(location.search).has("capture");
if (captureMode && hud) {
  // keep subtitles + shot tag, hide transport chrome for cleaner film frames
  hud.querySelector(".top")?.style.setProperty("display", "none");
  seek.style.display = "none";
}

seek.max = String(story.duration);

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true;
app.insertBefore(renderer.domElement, app.firstChild);

const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 80);
const { scene, update } = createFactoryScene(story);
const clock = new DirectorClock(story.duration);

function applyCamera(t) {
  const shot = shotAt(story, t);
  const { pos, target } = cameraPose(shot, t);
  // follow word box slightly in S03
  if (shot.camera.follow === "wordBoxForm" && t >= 18 && t < 26) {
    const follow = new THREE.Vector3(1.2, 1.0, 0.6);
    camera.position.set(pos[0], pos[1], pos[2]);
    camera.lookAt(follow.lerp(new THREE.Vector3(...target), 0.35));
  } else {
    camera.position.set(pos[0], pos[1], pos[2]);
    camera.lookAt(target[0], target[1], target[2]);
  }
  shotTag.textContent = `${shot.id} ${shot.name}`;
}

function applySubtitles(t) {
  const sub = subtitleAt(story, t);
  if (!sub) {
    subtitleEl.classList.remove("show");
    subtitleEl.textContent = "";
    return;
  }
  if (subtitleEl.textContent !== sub.text) subtitleEl.textContent = sub.text;
  subtitleEl.classList.add("show");
}

function setUi(t) {
  timeLabel.textContent = `${t.toFixed(1)} / ${story.duration.toFixed(1)}`;
  seek.value = String(t);
  playBtn.textContent = clock.playing ? "Pause" : "Play";
}

function frame(now) {
  const t = clock.tick(now);
  update(t);
  applyCamera(t);
  applySubtitles(t);
  setUi(t);
  renderer.render(scene, camera);
  requestAnimationFrame(frame);
}

playBtn.addEventListener("click", () => clock.toggle());
restartBtn.addEventListener("click", () => clock.restart());
seek.addEventListener("input", () => {
  clock.seek(Number(seek.value));
  clock.pause();
});

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

window.addEventListener("keydown", (e) => {
  if (e.code === "Space") {
    e.preventDefault();
    clock.toggle();
  }
});

// expose for capture script
window.__neuronFactory = {
  story,
  clock,
  seekTo: (t) => clock.seek(t),
  play: () => clock.play(),
  pause: () => clock.pause(),
  getTime: () => clock.t,
  canvas: () => renderer.domElement,
};

requestAnimationFrame(frame);
// autoplay for capture / demo
clock.play();
