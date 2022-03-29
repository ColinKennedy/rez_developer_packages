###################
Why Use rez_sphinx?
###################

`Sphinx`_ has been around for decades now so using any other tool over it, even
if that tool wraps `Sphinx`_, is a fair question. While "Why use rez_sphinx" is
a fair question, a better question would be "Is there anything `Sphinx`_ can do
better at"?

Assuming you use `Sphinx`_ or a similar "wrapper" tool, ask yourself these questions.

- Can you build documentation for your Rez package?
- Is setting up documentation for building an automated process?
- Is publishing the documentation fully automated as well?
- Is the published documentation safe from `link rot`_?
- Do you publish excessively? Or only when new features are introduced in a tool?
- Do you validate that documentation aren't just templates but real, hand-written pages?
- Can you customize the build / publish process across all packages and individually?
- Is the auto-generated API documentation always up to date and never accidentally wrong?
- Can you auto-add, build, and publish documentation on dozens of Rez packages, in batch?

If you answered all of those questions in a positive way, then you're already
set up for success. But if any of those points fall short and you'd like a
tool handle those things for you, :doc:`getting_started` is for you.

As you probably have guessed from the questions, `Sphinx`_ is great at building
individual tool documentation. But all of the logistical concerns, like how do
you make sure documentation is always build-able, kept up to date, is
automatically generated, and auto-links to dependency projects properly without
those links "rotting" in the future or getting accidentally overwritten -
`Sphinx`_ just can't handle any of those logistical concerns. Luckily though,
`Rez`_ is actually very well suited for the task.

:ref:`rez_sphinx` is the bridge between `Rez`_ and `Sphinx`_.

Interested? Check out :doc:`getting_started` next.
