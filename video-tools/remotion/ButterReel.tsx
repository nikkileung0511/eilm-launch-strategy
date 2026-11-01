// The Butter Edit graphics layer: opener title, item title cards, actor captions (Klasyczny
// stand-in), reaction pops and the location tag, composited over a pre-cut base video.
import React, { useEffect, useState } from "react";
import {
  AbsoluteFill,
  OffthreadVideo,
  continueRender,
  delayRender,
  interpolate,
  Easing,
  Sequence,
  staticFile,
  useCurrentFrame,
} from "remotion";

const C = {
  butter: "#F2C94C",
  plum: "#6B3A63",
  blush: "#E8669F",
  cream: "#FFF4D2",
  espresso: "#2B1E18",
};
const SERIF = "'Instrument Serif', Georgia, serif";
const SANS = "'Hanken Grotesk', Arial, sans-serif";
const CAPTION = "'Inter Tight', Arial, sans-serif"; // stand-in for Instagram Klasyczny

const FONTS: [string, string, string, string][] = [
  ["Instrument Serif", "instrument-serif-latin-400-normal.woff2", "400", "normal"],
  ["Instrument Serif", "instrument-serif-latin-400-italic.woff2", "400", "italic"],
  ["Hanken Grotesk", "hanken-grotesk-latin-500-normal.woff2", "500", "normal"],
  ["Hanken Grotesk", "hanken-grotesk-latin-600-normal.woff2", "600", "normal"],
  ["Hanken Grotesk", "hanken-grotesk-latin-800-normal.woff2", "800", "normal"],
  ["Inter Tight", "inter-tight-latin-600-normal.woff2", "600", "normal"],
];

const useBrandFonts = () => {
  const [handle] = useState(() => delayRender("Loading brand fonts"));
  useEffect(() => {
    Promise.all(
      FONTS.map(([family, file, weight, style]) => {
        const face = new FontFace(family, `url(${staticFile(`fonts/${file}`)})`, { weight, style });
        document.fonts.add(face);
        return face.load();
      }),
    ).then(() => continueRender(handle));
  }, [handle]);
};

export type Overlay =
  | { type: "opener"; from: number; dur: number; kicker: string; venue: string; sub: string }
  | { type: "card"; from: number; dur: number; plain: string; italic: string }
  | { type: "caption"; from: number; dur: number; text: string }
  | { type: "pop"; from: number; dur: number; text: string };

export type ButterReelProps = {
  video: string;
  totalFrames: number;
  location: string;
  overlays: Overlay[];
};

const outline = (px: number, color: string): React.CSSProperties => ({
  WebkitTextStroke: `${px}px ${color}`,
  paintOrder: "stroke fill",
});

const Opener: React.FC<{ kicker: string; venue: string; sub: string }> = ({ kicker, venue, sub }) => {
  const f = useCurrentFrame();
  const opacity = interpolate(f, [0, 6], [0, 1], { extrapolateRight: "clamp" });
  const [before, after] = kicker.split("★");
  return (
    <AbsoluteFill style={{ alignItems: "center", top: 560, opacity, textShadow: "0 0 36px rgba(0,0,0,.65)" }}>
      <div style={{ fontFamily: SERIF, fontSize: 58, letterSpacing: "0.04em", textTransform: "uppercase", color: C.cream, textAlign: "center", lineHeight: 1.1 }}>
        {before}
        {after !== undefined && <span style={{ color: C.blush }}>★</span>}
        {after}
      </div>
      <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 160, color: C.butter, lineHeight: 1, marginTop: 10, textShadow: "0 0 26px rgba(242,201,76,.6), 0 0 36px rgba(0,0,0,.5)" }}>
        {venue}
      </div>
      {sub && <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 36, color: "rgba(255,244,210,.9)", marginTop: 22 }}>{sub}</div>}
    </AbsoluteFill>
  );
};

const TitleCard: React.FC<{ plain: string; italic: string }> = ({ plain, italic }) => {
  const f = useCurrentFrame();
  const full = plain + italic;
  const shown = Math.min(full.length, Math.floor(f / 2) + 1); // 2 frames per character
  const p = full.slice(0, Math.min(shown, plain.length));
  const i = shown > plain.length ? full.slice(plain.length, shown) : "";
  return (
    <div style={{ position: "absolute", left: 140, top: 840, background: C.plum, color: C.cream, fontFamily: SERIF, fontSize: 64, lineHeight: 1, padding: "16px 28px 20px 44px", borderRadius: 4, whiteSpace: "pre" }}>
      <div style={{ position: "absolute", left: 14, top: 14, bottom: 14, width: 8, borderRadius: 8, background: C.butter }} />
      {p}
      <span style={{ fontStyle: "italic" }}>{i}</span>
    </div>
  );
};

const Caption: React.FC<{ text: string }> = ({ text }) => (
  <div style={{ position: "absolute", left: 130, right: 130, top: 1270, textAlign: "center", color: "#fff", fontFamily: CAPTION, fontWeight: 600, fontSize: 46, lineHeight: 1.12, letterSpacing: "-0.03em", whiteSpace: "pre-line", ...outline(8, "#000") }}>
    {text}
  </div>
);

const Pop: React.FC<{ text: string }> = ({ text }) => {
  const f = useCurrentFrame();
  const scale = interpolate(f, [0, 5], [1.2, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const opacity = interpolate(f, [0, 2], [0, 1], { extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", left: 96, right: 160, top: 600, color: C.butter, fontFamily: SANS, fontWeight: 800, fontSize: 64, lineHeight: 1.05, textTransform: "uppercase", transform: `rotate(-4deg) scale(${scale})`, transformOrigin: "left center", opacity, ...outline(6, C.espresso) }}>
      {text}
    </div>
  );
};

const LocationTag: React.FC<{ text: string }> = ({ text }) => (
  <div style={{ position: "absolute", left: 0, right: 0, top: 1540, textAlign: "center", color: "rgba(255,244,210,.82)", fontFamily: SERIF, fontStyle: "italic", fontSize: 34, textShadow: "0 0 14px rgba(0,0,0,.7)" }}>
    {text}
  </div>
);

export const ButterReel: React.FC<ButterReelProps> = ({ video, location, overlays }) => {
  useBrandFonts();
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <OffthreadVideo src={staticFile(video)} muted />
      {overlays.map((o, k) => (
        <Sequence key={k} from={o.from} durationInFrames={o.dur} layout="none">
          {o.type === "opener" && <Opener kicker={o.kicker} venue={o.venue} sub={o.sub} />}
          {o.type === "card" && <TitleCard plain={o.plain} italic={o.italic} />}
          {o.type === "caption" && <Caption text={o.text} />}
          {o.type === "pop" && <Pop text={o.text} />}
        </Sequence>
      ))}
      <LocationTag text={location} />
    </AbsoluteFill>
  );
};
