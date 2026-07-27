---
title: The $8,000 Contact Form
slug: the-8000-dollar-contact-form
date: 2026-07-26
author: Roman
read: 3 min read
kicker: Small Business Security
excerpt: Let me tell you a story. Fair warning up front: this is a composite, built from the kinds of incidents I see in security work, with details changed and blended. No real client, no real names. But every piece of it happens, constantly, to businesses this size.
---

Let me tell you a story. Fair warning up front: this is a composite, built from the kinds of incidents I see in security work, with details changed and blended. No real client, no real names. But every piece of it happens, constantly, to businesses this size.

## A form like every other form

Picture a small landscaping company. Ten years in business, good reviews, steady work. Their website has a contact form. Name, phone, email, "tell us about your project." The form was added by whoever built the site years ago, using a plugin that worked fine on day one.

The plugin was never updated. Why would it be? The form worked.

## The part nobody saw

Two years later, a security hole in that plugin version was published. Not secret knowledge. Public, documented, with a fix available. The fix never got installed, because nobody was watching.

Within weeks, automated scripts were sweeping the internet for sites running that exact version. One of them found the landscaping company. No person ever looked at the site. A script found the version number, matched it to the known hole, and used the form to plant a small file on the server.

That file sat quietly for months. Then it got put to work.

## The invoice that wasn't

The file gave someone access to the site's outgoing email. So when the company sent invoices, a copy went somewhere else too. Eventually, one of their commercial clients received a very normal-looking email: updated payment details, new bank account, please use this going forward. It matched the company's invoice format, because it was built from the company's real invoices.

The client paid $8,000 to the wrong account. Gone.

Here's the brutal part. The landscaping company didn't lose the money directly. They lost the client, who reasonably felt burned. They lost days untangling what happened. They paid to have the site cleaned and rebuilt. And they spent months wondering what else had leaked, because once someone's been inside, you don't get to know.

All of it traced back to one unpatched contact form.

## Small leaks become breaches

This is the thing I want small business owners to take from the story. Breaches at our scale almost never look like a dramatic hack. They look like a tiny neglected thing that compounds. A plugin nobody updated. A password reused from another account that leaked years ago. A backup file sitting in public. The initial hole is small. The consequence isn't.

And the fix, before the fact, is almost embarrassingly cheap. Updating a plugin costs nothing. Checking your site for known holes costs nothing. The $8,000 version only exists because the $0 version never happened.

## Check the form

I built Cerberus for exactly this. It's a scanner that checks small business websites for the boring, known, documented weaknesses that scripts exploit, including outdated software with published holes. The basic scan is free at [cerberusscan.com](https://cerberusscan.com) and takes about a minute.

If your website has a form on it, and it does, it's worth sixty seconds to find out what that form is running on.

*Questions about your results, or a site you're not sure has been maintained? Book a free 30-minute call at [ctfdesigns.com/book](https://ctfdesigns.com/book). I'd rather help you now than after.*
