from fsa import FSA, FSARenderer, State, EPSILON, FSAType

def example_1() -> FSA:
    q: list[State] = [State(f"q{i}") for i in range(4)]
    fsa: FSA = FSA(
        states=set(q),
        initial_state=q[0],
        final_states={q[3]},
        alphabet={"0", "1", "2"},
        transitions={
            (q[0], "0", q[1]),
            (q[1], "1", q[1]),
            (q[1], "1", q[2]),
            (q[1], "1", q[3]),
            (q[2], "1", q[3]),
            (q[2], "2", q[2]),
            (q[3], "0", q[2])
        }
    )

    return fsa

def example_2() -> FSA:
    q: list[State] = [State(f"q{i}") for i in range(3)]
    fsa: FSA = FSA(
        states=set(q),
        initial_state=q[0],
        final_states={q[2]},
        alphabet={"a", "b", "c"},
        transitions={
            (q[0], "a", q[0]),
            (q[0], EPSILON, q[1]),
            (q[1], EPSILON, q[1]),
            (q[1], EPSILON, q[2]),
            (q[2], "b", q[1]),
            (q[2], "c", q[2])
        }
    )

    return fsa

renderer: FSARenderer = FSARenderer()

renderer.render(example_2().epsilon_removal(), "example_1")