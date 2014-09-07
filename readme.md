# epsilon

An in-browser, non-linear personal notebook.

## Motivation
Here are some desirables:

 - A node (in the "knowledge graph") is a title, a set of tags, and some sequence of cards. A "card" is a block of content, basically a freeform text entry box that supports markdown. It can be moved up or down within the node, or moved to a different node, or split off into its own node.
 - The notebook is versioned. I am tempted to store snapshots of the entire collection of nodes, ala Git, but it seems useless to do this given that you can't do complicated changes. A change is basically always one of these actions:

     - add/remove a node
     - add/remove a tag from a node
     - change a node's title
     - add/remove a card from a node
     - change the position of a card within a node
     - change a card's content
     - move a card from one node to another
     - clone a card

  So probably I will just store the "deltas" of each change? Does this make sense? if I want to go to a previous revision, do I need to rewind all of the deltas? Is that prohibitive? The snapshot model does seem nice for this, because I can just check out past commits directly.

 - the notebook runs in the browser. it's an AJAX app that communicates with a backend running locally on the user's machine
 - there should be a powerful search and UX goodies like autocomplete when linking to other nodes

I like Gingko's emphasis on facilitating writing, but I feel like it fails to handle the earliest phase of knowledge acquisition/production, where you're trying to understand what's going on and only have a partial understanding. I like the idea of starting out with all of these disconnected nodes that you have partial understanding of, and as you integrate your knowledge and see more connections you can link them together. Like right now, I have a partial understanding of the "outer product" operator in geometric algebra. I understand a few of its isolated properties. It makes sense for me to write this partial understanding down in its own node. Later, when I see more of the picture, however, I probably want to re-arrange this by bringing my partial understandings together in a single node.
