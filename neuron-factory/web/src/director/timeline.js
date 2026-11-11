export function smoothstep(t) {
  const x = Math.min(1, Math.max(0, t));
  return x * x * (3 - 2 * x);
}

export function lerp(a, b, t) {
  return a + (b - a) * t;
}

export function lerp3(a, b, t) {
  return [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];
}

export function shotAt(story, t) {
  for (const shot of story.shots) {
    if (t >= shot.start && t < shot.end) return shot;
  }
  return story.shots[story.shots.length - 1];
}

export function cameraPose(shot, t) {
  const span = Math.max(0.001, shot.end - shot.start);
  const u = smoothstep((t - shot.start) / span);
  let pos = lerp3(shot.camera.from.pos, shot.camera.to.pos, u);
  const target = lerp3(shot.camera.from.target, shot.camera.to.target, u);
  if (shot.camera.orbit) {
    const ang = -0.35 + (t - shot.start) * 0.12;
    const radius = 4.4;
    const cx = 0;
    const cy = 1.15;
    const cz = -0.6;
    pos = [cx + Math.sin(ang) * radius, cy + 1.0, cz + Math.cos(ang) * radius];
  }
  return { pos, target, u };
}

export function subtitleAt(story, t) {
  return story.subtitles.find((s) => t >= s.start && t < s.end) || null;
}

export function eventProgress(story, type, t, predicate) {
  const ev = story.events.find(
    (e) => e.type === type && (!predicate || predicate(e))
  );
  if (!ev) return 0;
  if (type === "synapseGrow") {
    const dur = ev.duration || 12;
    return smoothstep((t - ev.t) / dur);
  }
  return t >= ev.t ? 1 : 0;
}

export class DirectorClock {
  constructor(duration) {
    this.duration = duration;
    this.t = 0;
    this.playing = false;
    this._last = 0;
  }

  play() {
    this.playing = true;
    this._last = performance.now();
  }

  pause() {
    this.playing = false;
  }

  toggle() {
    if (this.playing) this.pause();
    else this.play();
  }

  restart() {
    this.t = 0;
    this.play();
  }

  seek(t) {
    this.t = Math.min(this.duration, Math.max(0, t));
  }

  tick(now = performance.now()) {
    if (!this.playing) return this.t;
    const dt = (now - this._last) / 1000;
    this._last = now;
    this.t += dt;
    if (this.t >= this.duration) {
      this.t = this.duration;
      this.playing = false;
    }
    return this.t;
  }
}
