# The Anatomy of a GPT-5 Prompt

## Structure Overview

A well-structured AI prompt consists of six key components, each serving a specific purpose in guiding the AI's response:

## 1. **Role** 🎭

Define who the AI should act as - this sets the context and expertise level.

**Example:**
> Act as a personal productivity coach focused on recommending lesser-known, effective learning methods for mastering a new skill within three months.

## 2. **Task** 📋

Clearly outline what you want the AI to do. Break down complex requests into specific, actionable steps.

**Example:**
- Begin with a concise checklist (3-7 bullets) of steps you will follow, focusing on conceptual planning rather than lesson details.
- Identify and present the top 3 medium-commitment learning methods (not widely used) that can help someone make strong progress in under 90 days.
- Ensure each method offers a unique advantage through efficiency, engagement, or adaptability across skills.

## 3. **Context** 🌍

Provide boundaries, constraints, and additional information that shapes the response.

**Example:**
- Exclude common methods such as generic YouTube tutorials, mainstream MOOCs like Coursera/edX, or reading a standard textbook.
- Prioritize accuracy: Method names must match official or widely recognized sources, and time/resource estimates should be realistic.
- Highlight what makes each method an outstanding choice in a concise summary.

## 4. **Reasoning** 🧠

Guide the AI's thought process and quality assurance approach.

**Example:**
- Internally vet all methods to ensure they are real, underused, and meet all parameters before responding.
- Cross-check details and outcomes with credible learning or productivity sources.
- Optimize for clarity, concise presentation, and practical value.

## 5. **Output Format** 📊

Specify exactly how you want the response structured and presented.

**Example:**
Return results as a properly formatted Markdown table with these columns:

| Method name | Main resources | Weekly time: XX hrs | Estimated progress in 90 days | Summary |
|-------------|----------------|---------------------|-------------------------------|---------|
| [Method name] | [Main resources] | [Weekly time: XX hrs] | [Estimated progress in 90 days] | [Summary] |
| [Method name] | [Main resources] | [Weekly time: XX hrs] | [Estimated progress in 90 days] | [Summary] |
| [Method name] | [Main resources] | [Weekly time: XX hrs] | [Estimated progress in 90 days] | [Summary] |

## 6. **Stop Condition** 🛑

Define what constitutes a complete and successful response.

**Example:**
> Task is complete when three verified, unique medium-commitment methods are returned in the specified format, excluding overly common approaches, and validation confirms full compliance with requirements.

---

## Key Benefits of This Structure

- **Clarity**: Each component serves a distinct purpose
- **Control**: You guide the AI's approach and output
- **Quality**: Built-in validation and reasoning requirements
- **Consistency**: Reproducible results with clear expectations
- **Efficiency**: Reduces back-and-forth iterations

## Tips for Implementation

1. **Be Specific**: Vague instructions lead to generic responses
2. **Set Boundaries**: Use Context to exclude unwanted approaches
3. **Define Success**: Clear stop conditions prevent incomplete responses
4. **Request Reasoning**: Ask the AI to show its work for better quality
5. **Format Matters**: Structured outputs are easier to use and evaluate

---

*Source: evolving.ai - Advanced AI prompt engineering techniques*