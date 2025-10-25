# Contributing to Senior AI Infrastructure Engineer Learning Repository

Thank you for your interest in contributing to the AI Infrastructure Career Path Curriculum! This repository is a community-driven educational resource, and we welcome contributions from learners, educators, and industry professionals.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Contribution Guidelines](#contribution-guidelines)
- [Content Quality Standards](#content-quality-standards)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Review Process](#review-process)
- [Community](#community)
- [Recognition](#recognition)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Experience level (from beginners to experts)
- Educational background
- Gender identity and expression
- Sexual orientation
- Disability
- Personal appearance
- Race or ethnicity
- Age
- Religion or lack thereof
- Nationality

### Our Standards

**Positive behaviors include**:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members
- Providing and accepting constructive feedback

**Unacceptable behaviors include**:
- Harassment, trolling, or discriminatory comments
- Publishing others' private information without permission
- Personal attacks or political arguments
- Other conduct which could reasonably be considered inappropriate in a professional setting

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team at ai-infra-curriculum@joshua-ferguson.com. All complaints will be reviewed and investigated promptly and fairly.

---

## How Can I Contribute?

There are many ways to contribute to this curriculum:

### 1. Content Improvements

**Module Content**:
- Improve lecture notes clarity and accuracy
- Add more detailed explanations
- Create additional examples and use cases
- Update content to reflect latest technologies
- Fix technical inaccuracies

**Labs and Exercises**:
- Improve lab instructions
- Add hints and troubleshooting tips
- Create alternative exercises
- Add difficulty variations (easier/harder)

**Documentation**:
- Fix typos and grammatical errors
- Improve README files
- Add troubleshooting guides
- Create quick reference sheets
- Translate documentation (future)

### 2. Code Contributions

**Code Stubs**:
- Improve code stub templates
- Add more detailed TODO comments
- Fix bugs in starter code
- Add type hints and documentation

**Test Cases**:
- Add more comprehensive test cases
- Improve test coverage
- Add integration tests
- Create performance benchmarks

**Scripts and Tools**:
- Create helper scripts for setup
- Build automation tools
- Develop debugging utilities
- Add CI/CD improvements

### 3. New Content

**Additional Labs**:
- Create supplementary exercises
- Add advanced challenges
- Build mini-projects
- Create integration exercises

**Resources**:
- Curate relevant articles and papers
- Add book recommendations
- Create cheat sheets
- Build reference guides

**Examples**:
- Add real-world examples
- Share case studies
- Create demo projects
- Build reference implementations

### 4. Community Support

**Help Others**:
- Answer questions in discussions
- Review pull requests
- Provide feedback on issues
- Share your learning experiences

**Create Content**:
- Write blog posts about your learning
- Create video tutorials
- Share solutions to challenging labs
- Document common pitfalls and solutions

### 5. Feedback and Testing

- Report bugs and issues
- Suggest improvements
- Test new content
- Provide user experience feedback

---

## Getting Started

### Prerequisites for Contributing

1. **GitHub Account**: Required for all contributions
2. **Git Knowledge**: Basic git commands and workflow
3. **Development Environment**: Set up as per repository README
4. **Understanding**: Read through relevant modules before contributing

### Setup for Development

```bash
# 1. Fork the repository on GitHub
# Click the "Fork" button at https://github.com/ai-infra-curriculum/ai-infra-senior-engineer-learning

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/ai-infra-senior-engineer-learning.git
cd ai-infra-senior-engineer-learning

# 3. Add upstream remote
git remote add upstream https://github.com/ai-infra-curriculum/ai-infra-senior-engineer-learning.git

# 4. Create a branch for your contribution
git checkout -b feature/your-feature-name

# 5. Make your changes
# ... edit files ...

# 6. Commit your changes
git add .
git commit -m "Description of your changes"

# 7. Push to your fork
git push origin feature/your-feature-name

# 8. Create a Pull Request on GitHub
```

### Finding Issues to Work On

**Good First Issues**:
- Look for issues labeled `good-first-issue`
- These are beginner-friendly contributions
- Great for first-time contributors

**Help Wanted**:
- Issues labeled `help-wanted` need community assistance
- May require more experience or time commitment

**Content Gaps**:
- Check issues labeled `content-improvement`
- Look for TODOs in code and documentation

---

## Contribution Guidelines

### Before You Start

1. **Check Existing Issues**: Search issues to avoid duplicates
2. **Create an Issue**: For significant changes, create an issue first to discuss
3. **Claim the Issue**: Comment on the issue to let others know you're working on it
4. **Ask Questions**: If unclear, ask in the issue comments

### Types of Contributions

#### Bug Fixes

**What qualifies as a bug**:
- Incorrect technical information
- Broken code examples
- Non-functional labs or exercises
- Broken links or references
- Formatting issues

**Bug fix process**:
1. Create an issue describing the bug (if not already reported)
2. Reference the issue in your PR
3. Include steps to reproduce (if applicable)
4. Test your fix thoroughly

#### Content Enhancements

**Examples**:
- Adding more detailed explanations
- Creating additional examples
- Improving code comments
- Adding diagrams or visualizations

**Requirements**:
- Must maintain consistency with existing content style
- Should be technically accurate and up-to-date
- Include references for technical claims

#### New Features

**Examples**:
- New lab exercises
- Additional modules or sections
- New tools or scripts
- Enhanced CI/CD workflows

**Requirements**:
- Discuss in an issue before implementing
- Must align with curriculum goals
- Requires comprehensive documentation
- Needs appropriate tests

---

## Content Quality Standards

### Technical Accuracy

1. **Verify Information**: All technical content must be accurate and current
2. **Test Code**: All code examples must be tested and working
3. **Reference Sources**: Cite authoritative sources for technical claims
4. **Version Specificity**: Specify versions for tools and frameworks

### Clarity and Accessibility

1. **Clear Writing**: Use clear, concise language
2. **Define Terms**: Define technical terms on first use
3. **Progressive Complexity**: Build from simple to complex
4. **Examples**: Include concrete examples for abstract concepts

### Consistency

1. **Style Guide**: Follow existing formatting and style conventions
2. **Naming Conventions**: Use consistent naming across files
3. **Structure**: Maintain consistent file and directory structure
4. **Terminology**: Use consistent technical terminology

### Inclusivity

1. **Accessible Language**: Avoid jargon where simpler terms work
2. **Diverse Examples**: Use diverse names and scenarios in examples
3. **Multiple Learning Styles**: Include text, diagrams, and code
4. **Prerequisites**: Clearly state prerequisites and provide references

---

## Pull Request Process

### Before Submitting

1. **Test Your Changes**: Ensure all code works as expected
2. **Run Linters**: Fix any linting errors
3. **Update Documentation**: Update relevant docs
4. **Check Formatting**: Ensure consistent formatting
5. **Review Your Changes**: Do a self-review before submitting

### PR Title and Description

**Title Format**: `[Type] Brief description`

**Types**:
- `[Fix]` - Bug fixes
- `[Feat]` - New features
- `[Docs]` - Documentation changes
- `[Style]` - Formatting, no code change
- `[Refactor]` - Code refactoring
- `[Test]` - Adding or updating tests
- `[Chore]` - Maintenance tasks

**Example**: `[Feat] Add advanced GPU profiling lab to Module 203`

**Description Template**:
```markdown
## Description
Brief description of what this PR does and why.

## Related Issue
Fixes #123 (if applicable)

## Changes Made
- List of specific changes
- Another change
- And another

## Testing
Describe how you tested these changes:
- Test 1
- Test 2

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass
- [ ] No new warnings
```

### PR Size

**Keep PRs Focused**:
- One logical change per PR
- Smaller PRs are easier to review
- If making multiple changes, create multiple PRs

**Size Guidelines**:
- Small: <100 lines changed (preferred)
- Medium: 100-500 lines changed
- Large: >500 lines changed (should be split if possible)

### Review Process

1. **Automated Checks**: CI/CD must pass
2. **Peer Review**: At least one approval required
3. **Maintainer Review**: Final review by maintainer
4. **Revisions**: Address feedback and update PR
5. **Merge**: Maintainer merges once approved

### After Merge

- Your contribution will be credited in release notes
- Close any related issues
- Celebrate! You've contributed to the community

---

## Issue Reporting

### Creating Good Issues

**Issue Title**: Clear, concise, specific
- Good: "Module 203 Lab 2 - CUDA code fails to compile on Ubuntu 22.04"
- Bad: "Lab doesn't work"

**Issue Description**: Include:
1. **Description**: What's the issue?
2. **Expected Behavior**: What should happen?
3. **Actual Behavior**: What actually happens?
4. **Steps to Reproduce**: How to recreate the issue?
5. **Environment**: OS, versions, etc.
6. **Screenshots/Logs**: If applicable

### Issue Template

```markdown
## Description
A clear description of the issue.

## Expected Behavior
What should happen?

## Actual Behavior
What actually happens?

## Steps to Reproduce
1. Step one
2. Step two
3. ...

## Environment
- OS: Ubuntu 22.04
- Python: 3.11.2
- Kubernetes: 1.27
- Other relevant info

## Additional Context
Any other context, screenshots, or logs.
```

### Issue Labels

We use labels to categorize issues:
- `bug` - Something isn't working
- `documentation` - Documentation improvements
- `enhancement` - New feature or request
- `good-first-issue` - Good for newcomers
- `help-wanted` - Extra attention needed
- `question` - Further information requested
- `content-improvement` - Content quality issues

---

## Testing Requirements

### Code Testing

**All code contributions must include tests**:

1. **Unit Tests**: Test individual functions/classes
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows

**Testing Framework**: pytest

**Example Test Structure**:
```python
# tests/test_training.py
import pytest
from src.training import TrainingPipeline

class TestTrainingPipeline:
    """Test cases for TrainingPipeline"""

    def test_pipeline_initialization(self):
        """Test pipeline initializes correctly"""
        pipeline = TrainingPipeline(config={})
        assert pipeline is not None

    def test_pipeline_with_invalid_config(self):
        """Test pipeline handles invalid config"""
        with pytest.raises(ValueError):
            TrainingPipeline(config={"invalid": "config"})
```

**Running Tests**:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_training.py

# Run with coverage
pytest --cov=src tests/
```

**Coverage Requirements**:
- New code should have >80% test coverage
- Critical paths should have 100% coverage

### Documentation Testing

**Check Documentation**:
```bash
# Check markdown formatting
markdownlint **/*.md

# Check spelling
codespell **/*.md

# Check links
markdown-link-check **/*.md
```

### Manual Testing

For labs and exercises:
1. **Follow Instructions**: Complete the lab from scratch
2. **Verify Output**: Ensure expected results
3. **Test Edge Cases**: Try invalid inputs, error conditions
4. **Document Issues**: Note any problems encountered

---

## Documentation Standards

### Markdown Style

**Headers**:
```markdown
# Top Level (H1) - Used for page title only
## Second Level (H2) - Major sections
### Third Level (H3) - Subsections
#### Fourth Level (H4) - Sub-subsections
```

**Code Blocks**:
````markdown
```python
# Always specify language for syntax highlighting
def example_function():
    return "Use 4-space indentation"
```
````

**Links**:
```markdown
<!-- Use descriptive link text -->
See the [advanced topics guide](./advanced-topics.md) for more details.

<!-- Not this -->
Click [here](./advanced-topics.md).
```

**Lists**:
```markdown
<!-- Use consistent markers -->
- Item one
- Item two
  - Nested item
  - Another nested item
- Item three

<!-- For ordered lists -->
1. First step
2. Second step
3. Third step
```

### Code Documentation

**Python Docstrings** (Google style):
```python
def train_model(model, data, epochs=10):
    """Train a machine learning model.

    This function trains the provided model on the given data
    for the specified number of epochs.

    Args:
        model: The model to train (PyTorch nn.Module)
        data: Training data (DataLoader)
        epochs: Number of training epochs (default: 10)

    Returns:
        Trained model with updated weights

    Raises:
        ValueError: If epochs is not positive
        RuntimeError: If GPU is required but not available

    Example:
        >>> model = MyModel()
        >>> data = DataLoader(dataset)
        >>> trained = train_model(model, data, epochs=5)
    """
    pass
```

**Comments**:
```python
# Good: Explain why, not what
# Using exponential learning rate decay to prevent overshooting
scheduler = ExponentialLR(optimizer, gamma=0.95)

# Bad: Stating the obvious
# Create a scheduler
scheduler = ExponentialLR(optimizer, gamma=0.95)
```

### README Standards

Every directory should have a README that includes:
1. **Purpose**: What this directory/component does
2. **Contents**: What's included
3. **Usage**: How to use it
4. **Prerequisites**: What's needed
5. **Examples**: Basic usage examples

---

## Review Process

### What Reviewers Look For

**Technical Correctness**:
- Is the information accurate?
- Does the code work?
- Are there edge cases not handled?

**Code Quality**:
- Is the code readable?
- Are there appropriate comments?
- Is it well-structured?
- Does it follow best practices?

**Documentation**:
- Are changes documented?
- Are docstrings complete?
- Is the README updated?

**Testing**:
- Are there adequate tests?
- Do tests pass?
- Is coverage sufficient?

**Consistency**:
- Does it match existing style?
- Are naming conventions followed?
- Is it consistent with curriculum goals?

### Responding to Feedback

**Be Receptive**:
- Reviews help improve the project
- Reviewers are volunteering their time
- Treat feedback as learning opportunities

**Be Responsive**:
- Respond to feedback promptly
- Ask questions if feedback is unclear
- Make requested changes or explain why not

**Be Collaborative**:
- Discuss alternatives if you disagree
- Seek consensus
- Be willing to compromise

### Becoming a Reviewer

Want to help review PRs?
1. Demonstrate quality contributions
2. Show understanding of curriculum goals
3. Be constructive and helpful in reviews
4. Contact maintainers to express interest

---

## Community

### Communication Channels

**GitHub Discussions**:
- Best for: In-depth technical discussions, questions
- Response time: 24-48 hours typically

**Slack Workspace**:
- Best for: Quick questions, real-time collaboration
- Channel: #senior-engineer-learning

**Office Hours**:
- When: Fridays 2-3pm PST
- Format: Live Q&A, code reviews
- Join: Link in Slack

**Email**:
- For: Private matters, conduct violations
- Address: ai-infra-curriculum@joshua-ferguson.com

### Community Guidelines

**Be Helpful**:
- Share knowledge generously
- Welcome newcomers
- Answer questions patiently

**Be Respectful**:
- Respect different experience levels
- Value diverse perspectives
- Assume good intent

**Be Professional**:
- Keep discussions technical
- Avoid off-topic debates
- Focus on constructive feedback

---

## Recognition

We value all contributions and recognize contributors in several ways:

### Contributors List

All contributors are listed in:
- Repository CONTRIBUTORS.md file
- Release notes for their contributions
- Annual contributor highlights

### Types of Recognition

**Code Contributors**:
- GitHub contributors page
- Credit in release notes

**Content Contributors**:
- Attribution in improved modules
- Mentioned in changelog

**Community Leaders**:
- Featured in newsletter
- Special recognition badge
- Invitation to maintainer team

### Contributor Levels

**Bronze**: 1-5 merged PRs
**Silver**: 6-15 merged PRs
**Gold**: 16+ merged PRs
**Platinum**: Sustained contribution over 6+ months

### Special Recognition

**Top Contributor of the Month**:
- Featured on README
- Mentioned in social media
- Small token of appreciation

---

## Questions?

**Not sure where to start?**
- Check out `good-first-issue` labels
- Ask in GitHub Discussions
- Attend office hours

**Have an idea but not sure if it fits?**
- Create an issue to discuss
- Ask in Slack #senior-engineer-learning

**Need help with your contribution?**
- Ask in the PR comments
- Post in GitHub Discussions
- Reach out in Slack

**Found a security issue?**
- Email ai-infra-curriculum@joshua-ferguson.com
- Do not create public issue
- We'll respond within 48 hours

---

## License

By contributing, you agree that your contributions will be licensed under the same [MIT License](LICENSE) that covers this project.

---

## Thank You!

Every contribution, no matter how small, makes this curriculum better for everyone. Whether you're fixing a typo, improving a lab, or adding new content, your effort helps thousands of learners worldwide.

Thank you for being part of this community!

---

**Ready to contribute? Check out our [open issues](https://github.com/ai-infra-curriculum/ai-infra-senior-engineer-learning/issues) or create a new one!**
