"""Custom CSS for the app."""

CSS = """
<style>
.block-container { padding-top: 2rem; max-width: 1100px; }
.hero {
    padding: 2rem 2.2rem; border-radius: 20px; margin-bottom: 1.2rem;
    background: radial-gradient(circle at 15% 20%, rgba(29,185,84,.35), transparent 45%),
                radial-gradient(circle at 85% 80%, rgba(179,136,255,.30), transparent 50%),
                linear-gradient(135deg, #151a2b, #0e1117);
    border: 1px solid rgba(255,255,255,.08);
}
.hero h1 { margin: 0; font-size: 2.4rem; letter-spacing: -.5px; }
.hero p { margin: .4rem 0 0; color: #aab1c5; font-size: 1.05rem; }
.badge {
    display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: .72rem;
    font-weight: 600; margin-right: 6px; color: #0e1117;
}
.badge.ghost { background: rgba(255,255,255,.08); color: #c9cfe0; font-weight: 500; }
.t-title { font-size: 1.05rem; font-weight: 700; line-height: 1.25; }
.t-sub { color: #98a0b5; font-size: .85rem; margin-bottom: 6px; }
.bars { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 6px; }
.bar-label { font-size: .68rem; color: #98a0b5; text-transform: uppercase; letter-spacing: .5px; }
.bar { height: 6px; border-radius: 6px; background: rgba(255,255,255,.08); overflow: hidden; }
.bar > span { display: block; height: 100%; border-radius: 6px; background: linear-gradient(90deg,#1DB954,#7be3a0); }
.stat {
    padding: 1rem 1.2rem; border-radius: 14px; background: #171B26;
    border: 1px solid rgba(255,255,255,.06);
}
.stat .n { font-size: 1.6rem; font-weight: 800; }
.stat .l { color: #98a0b5; font-size: .8rem; }
.persona {
    padding: 1.6rem 2rem; border-radius: 20px; text-align: center; margin-bottom: 1rem;
    background: linear-gradient(135deg, rgba(29,185,84,.18), rgba(179,136,255,.18));
    border: 1px solid rgba(255,255,255,.1);
}
.persona .emoji { font-size: 3rem; }
.persona h2 { margin: .2rem 0; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 14px; }
button[kind="secondary"] { border-radius: 10px; }
</style>
"""
