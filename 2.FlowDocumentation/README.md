# Part 2: Flow Documentation

## Setup

Step 0. [Download the `flow-documentation` extension](../README.md).

Step 1. Open VSCode in the `shopping-app` folder.

Step 2. Launch the 5 microservice (user, product, cart, order, payment) in debug mode by using the predefined `Debug All Microservices` configuration (`Ctrl + P` to open symbol navigator, then `Debug All Microservices`).

Step 3. Wait until the microservices are launched, then run `website_microservice/website.py`. There should be no errors, and you should see a text in the console reading `Purchase completed successfully.`.

Step 4. If everything goes well, you can stop the microservices and start exploring the code in `website_microservice/website.py` using `Flow Graphs`!

## Features

The `Flow Documentation` sidebar contains a button to Fetch the Flows in your project, which will display them in a list.

You can either create a new flow by adding the `# flow-start(<flow-name>)` comment before a function header or use the predefined flow `buy-app` as an example.

After creating a graph for the `buy-app` flow, you can explore by right-clicking either:
- a node in the graph: opens the function definition in the editor.
- an edge in the graph: opens the code line where the source function calls the destination function.
- a line of python code (followed by `Highlight in Flow Graph`): briefly highlights the function which is called in that line of code (or the function which contains the line of code, if the line of code does not contain a function call).
