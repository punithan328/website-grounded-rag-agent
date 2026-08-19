def test_chainlit_graph_can_be_created():
    
    from app.agent.graph import build_graph

    graph = build_graph()

    assert graph is not None