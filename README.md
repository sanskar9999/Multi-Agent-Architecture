# Multi-Agent Architecture 

This project employs a systematic approach to problem-solving, integrating specialized modules for effective task handling. This architecture aims that every aspect of a given problem is addressed through LLMs to offer comprehensive solutions.

![Multi-Agent Architecture](MAA.png)

[Multi-Agent Architecture Google Colab Notebook](https://colab.research.google.com/drive/1oSc_diSLUJKwhWtf9eEg1j5flq3LEfeY?usp=sharing)

## System Workflow

1. **Problem Definer Agent**

- Clarifies user's objectives.
- Ensures clear understanding through iterative clarifying questions.
- Passes well-defined problems to the Decomposer Agent.

2. **Decomposer Agent**

- Breaks down problems into manageable subtasks.
- Explores alternative choices for each subtask.
- Passes individual subtasks to the Generator Agent.

3. **Generator Agent**

- Determines the number of Worker Agents needed.
- Generates custom prompts specifying individual tasks for each Worker Agent.
- Sends output to respective Worker Agents.

4. **Worker Agents**

- Specialized in solving specific subtasks (coding, analysis, data manipulation, etc.)
- Plans and explains reasoning step by step.
- Iterates on individual problems until correct solutions are found.

5. **Compiler Agent**

- Combines solutions from Worker Agents into a unified final solution.
- Evaluates and selects the most promising combined solution.

6. **Tester Agent**

- Executes and evaluates the final solution against original problem objectives.
- Provides detailed feedback on strengths and weaknesses.

7. **Error Identifier**

* Identifies issues or flaws in the solution based on Tester's feedback
* Categorizes errors or flaws
* Prioritizes errors based on their impact

8. **Editor Agent**

* Suggests edits or improvements based on identified errors
* Iterates editing process based on Tester's feedback
* Enhances workflow efficiency

## How It Works

The human user inputs their raw prompt to The Problem Definer agent which clarifies objectives through questions; this defined problem is then broken down by the Decomposer agent into smaller parts until they are manageable; these parts are assigned as tasks to specialized Worker Agents by the Generator agent; solutions from worker agents are compiled into a unified answer by Compiler agent; this answer is tested against original objectives by Tester agent; if an error is found it's identified by Error Identifier agent which sends details to the Editor agent which takes the error details into consideration and suggests improvements to the breaking down agent, this loop runs till the final answer is satisfied as correct by the Tester agent and if it it correct then its sent out as the output.
