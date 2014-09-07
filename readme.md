# epsilon

An in-browser, non-linear personal notebook.

## Motivation
Here are some desirables:

 - A page is a title, a set of tags, and some sequence of cards. A "card" is a block of content, basically a freeform text entry box that supports markdown. It can be moved up or down within the page, or moved to a different page, or split off into its own page.
 - The notebook is versioned. I am tempted to store snapshots of the entire collection of pages, ala Git, but it seems useless to do this given that you can't do complicated changes. A change is basically always one of these actions:

     - add/remove a page
     - add/remove a tag from a page
     - change a page's title
     - add/remove a card from a page
     - change the position of a card within a page
     - change a card's content
     - move a card from one page to another
     - clone a card

  So probably I will just store the "deltas" of each change? Does this make sense? if I want to go to a previous revision, do I need to rewind all of the deltas? Is that prohibitive? The snapshot model does seem nice for this, because I can just check out past commits directly.

It seems like it would be simplest if each page were individually versioned

 - the notebook runs in the browser. it's an AJAX app that communicates with a backend running locally on the user's machine
 - there should be a powerful search and UX goodies like autocomplete when linking to other pages

I like Gingko's emphasis on facilitating writing, but I feel like it fails to handle the earliest phase of knowledge acquisition/production, where you're trying to understand what's going on and only have a partial understanding. I like the idea of starting out with all of these disconnected pages that you have partial understanding of, and as you integrate your knowledge and see more connections you can link them together. Like right now, I have a partial understanding of the "outer product" operator in geometric algebra. I understand a few of its isolated properties. It makes sense for me to write this partial understanding down in its own page. Later, when I see more of the picture, however, I probably want to re-arrange this by bringing my partial understandings together in a single page.

## storage/data model

theres an object store, much like git's, for storing hashed content.

Page Revision object is:

 - a hash of the page title
 - a list of hashes of cards
 - date and time

Web state object is:

 - a list of Tagged Page data, each entry consisting of a (page id, page revision) pair and a (sorted) list of hashes of tag names
 - hash of the previous Web state object?
 - date and time

So the the object store is compressed content indexed by hashes. it stores page titles, tag names, card content, page revision objects and web commit objects

Outside of the object store we have separate data structures:

each Page is a page id and a table of two columns: (revision number, revision hash).

so we have a HEAD page somewhere with just the hash of the current state of the web.

### unsure

 - whether tag data should be part of Page Revision data or not. it kind of seems like when I'm tagging something, I'm not changing the page itself, only its metadata.
