"""Property-based tests: render_frame invariants and Style validation."""

import re

from hypothesis import given, settings
from hypothesis import strategies as st

from progz.renderer import render_frame
from progz.styles import Component, Style

_ANSI = re.compile(r"\033\[[0-9;]*m")

_rgb = st.tuples(st.integers(0, 255), st.integers(0, 255), st.integers(0, 255))

_EIGHTHS = ("▏", "▎", "▍", "▌", "▋", "▊", "▉")


@st.composite
def _styles(draw):
    thresholds = sorted(
        draw(
            st.lists(
                st.floats(0.0, 1.0, allow_nan=False),
                unique=True,
                min_size=1,
                max_size=4,
            )
        )
    )
    return Style(
        layout=tuple(draw(st.lists(st.sampled_from(list(Component)), unique=True, max_size=9))),
        bar_width=draw(st.integers(1, 60)),
        fill_text=draw(st.text(alphabet=st.characters(min_codepoint=33, max_codepoint=126), max_size=10)),
        color_stops=tuple((t, draw(_rgb)) for t in thresholds),
        interpolate=draw(st.booleans()),
        color_by_position=draw(st.booleans()),
        block_chars=draw(st.sampled_from(((), _EIGHTHS))),
    )


@given(
    style=_styles(),
    completed=st.integers(0, 10**9),
    total=st.none() | st.integers(0, 10**9),
    elapsed=st.floats(0.0, 1e12, allow_nan=False),
    # Rate floor excludes denormals: a rate below one step per ~11 days
    # renders an ETA with hundreds of digits, which only the terminal
    # width cap in ProgressBar._draw is responsible for containing.
    rate=st.none() | st.floats(1e-6, 1e9, allow_nan=False),
    # The description is rendered verbatim, so keep the strategy free of
    # ESC; a user-supplied escape byte is not the renderer leaking ANSI.
    description=st.text(alphabet=st.characters(min_codepoint=32), max_size=20),
    use_color=st.booleans(),
)
@settings(deadline=None, max_examples=100)
def test_render_frame_invariants(style, completed, total, elapsed, rate, description, use_color):
    out = render_frame(completed, total, elapsed, description, style, use_color, rate)

    # No ANSI when color is off.
    if not use_color:
        assert "\033" not in out

    # Visible width never exceeds the layout's worst case: one bar, the
    # fill text, the description, and bounded readouts plus separators
    # (count 21, ETA 20, elapsed 15, rate 12, percent 4, spinner 1,
    # eight separators).
    visible = _ANSI.sub("", out)
    assert len(visible) <= style.bar_width + len(style.fill_text) + len(description) + 100

    # Any color escape is eventually reset; no color leaks past the frame.
    last_color = out.rfind("\033[38")
    if last_color != -1:
        assert out.find("\033[0m", last_color) != -1

    # Purity: same inputs, same output.
    assert out == render_frame(completed, total, elapsed, description, style, use_color, rate)


@given(
    stops=st.lists(
        st.tuples(st.floats(allow_nan=True, allow_infinity=True), _rgb)
    ).map(tuple)
)
@settings(deadline=None, max_examples=100)
def test_style_stops_construct_or_valueerror(stops):
    try:
        Style(color_stops=stops)
    except ValueError:
        pass
