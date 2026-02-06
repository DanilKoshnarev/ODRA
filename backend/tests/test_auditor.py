"""Tests for auditor service."""
import pytest
from app.services.auditor import AuditorPlanner


def test_auditor_planner_initialization():
    """Test auditor planner initialization."""
    goal = "Find suspicious purchases"
    planner = AuditorPlanner(goal, scope="Finance")
    
    assert planner.goal == goal
    assert planner.scope == "Finance"
    assert planner.iteration == 0
    assert planner.max_iterations == 5


def test_decompose_goal():
    """Test goal decomposition."""
    goal = "Find suspicious purchases 2024"
    planner = AuditorPlanner(goal)
    
    subqueries = planner.decompose_goal()
    
    assert len(subqueries) > 0
    assert goal in subqueries[0]


@pytest.mark.asyncio
async def test_vector_search():
    """Test vector search."""
    planner = AuditorPlanner("Test goal")
    results = await planner.vector_search("test query", top_k=5)
    
    # Should return list, possibly empty if no documents
    assert isinstance(results, list)


def test_synthesis_prompt_building():
    """Test synthesis prompt building."""
    planner = AuditorPlanner("Test goal")
    evidence = [
        {
            "title": "Document 1",
            "snippet": "Suspicious activity detected",
            "score": 0.95,
        }
    ]
    
    prompt = planner._build_synthesis_prompt("Test goal", evidence)
    
    assert "Test goal" in prompt
    assert "suspicious activity" in prompt.lower()


def test_recommendations_generation():
    """Test recommendations generation."""
    planner = AuditorPlanner("Test goal")
    evidence = [{"title": "doc1", "score": 0.9}]
    summary = "Found issues in documents"
    
    recommendations = planner._generate_recommendations(summary, evidence)
    
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
