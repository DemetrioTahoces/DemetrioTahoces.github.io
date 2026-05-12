"""Quick test script for the agent."""
import asyncio
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from core.agent import create_agent_graph


async def test():
    graph = create_agent_graph()

    # Test 1: CV question (should use tools)
    print("=" * 60)
    print("TEST 1: CV question")
    print("=" * 60)
    result = await graph.ainvoke(
        {"messages": [("user", "Donde trabaja Demetrio actualmente?")]},
        config={"configurable": {"thread_id": "test1"}},
    )
    for m in result["messages"]:
        tool_calls = getattr(m, "tool_calls", [])
        content_preview = str(m.content)[:200] if m.content else "(empty)"
        print(f"  [{m.type}] tool_calls={len(tool_calls)} | {content_preview}")
    print()

    # Test 2: Off-topic (should reject without tools)
    print("=" * 60)
    print("TEST 2: Off-topic question")
    print("=" * 60)
    result2 = await graph.ainvoke(
        {"messages": [("user", "Cual es la capital de Francia?")]},
        config={"configurable": {"thread_id": "test2"}},
    )
    for m in result2["messages"]:
        tool_calls = getattr(m, "tool_calls", [])
        content_preview = str(m.content)[:200] if m.content else "(empty)"
        print(f"  [{m.type}] tool_calls={len(tool_calls)} | {content_preview}")
    print()

    # Test 3: Companies enumeration
    print("=" * 60)
    print("TEST 3: Companies enumeration")
    print("=" * 60)
    result3 = await graph.ainvoke(
        {"messages": [("user", "En qué empresas ha trabajado Demetrio?")]},
        config={"configurable": {"thread_id": "test_empresas"}},
    )
    for m in result3["messages"]:
        tool_calls = getattr(m, "tool_calls", [])
        content_preview = str(m.content)[:400] if m.content else "(empty)"
        print(f"  [{m.type}] tool_calls={len(tool_calls)} | {content_preview}")


if __name__ == "__main__":
    asyncio.run(test())
