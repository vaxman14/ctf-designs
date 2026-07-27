---
title: What a Website Security Scan Actually Checks (in English)
slug: what-a-website-security-scan-checks
date: 2026-07-26
author: Roman
read: 3 min read
kicker: Small Business Security
excerpt: "Security scan" sounds like something out of a movie. Green text, a progress bar, a voice saying "we're in."
---

"Security scan" sounds like something out of a movie. Green text, a progress bar, a voice saying "we're in."

The reality is less cinematic and a lot more useful. A good scan is basically a home inspection for your website. It walks around the property, checks the locks, looks for the stuff a burglar would look for, and hands you a report. No drama, just findings.

I run these scans constantly through Cerberus, my security scanner for small business sites. Here's what one actually checks, translated into English.

## The padlock (SSL/HTTPS)

This is the lock on your front door. When your site runs on HTTPS, everything between your visitor and your site is encrypted. A scan checks that the certificate exists, that it's valid, that it isn't about to expire, and that your site isn't quietly serving some pages without it. An expired certificate doesn't just weaken security. It throws a full-screen browser warning that scares off every visitor you paid to get.

## Security headers

These are instructions your site sends to every browser that visits, telling it things like "don't let anyone embed this site in a fake frame" and "only load scripts from places I trust." They cost nothing, take minutes to set up, and most small business sites are missing most of them. A scan lists exactly which ones you have and which you don't.

## Exposed files

This one surprises people. Websites often have files sitting in public that were never meant to be seen. Backup copies, configuration files with passwords in them, lists of every file on the server, old versions of pages. Nobody linked to them, so the owner assumes they're hidden. They're not. Bots guess these locations all day long, because the locations are predictable. A scan guesses them first, so you find out before someone else does.

## Outdated software

If your site runs on a platform like WordPress, every plugin and theme is a potential door. When a hole is found in one, it gets published, patched, and then immediately weaponized against every site that didn't update. A scan identifies what your site is running and flags versions with known problems. This is the single most common way small business sites get taken over.

## Leaking information

Little things that tell an attacker more than you'd want: server version numbers on error pages, email addresses harvestable by spam bots, directory listings left open. Individually small. Together, a map of your property drawn for a stranger.

## What a scan is not

Honesty matters here. A scan is not a guarantee. It checks the doors and windows. It can't promise nobody clever will ever get in, and anyone who sells you a scan as "hacker-proof certification" is selling you something else. What it does is close the gap between you and the automated attacks that account for the vast majority of small business breaches. That's a big gap, and it's the one that actually matters at our size.

## The good news

Almost everything a scan finds is fixable in an afternoon. These aren't exotic problems. They're maintenance items, like a gutter that needs clearing.

If you've never had your site checked, the free scan at [cerberusscan.com](https://cerberusscan.com) takes about a minute and gives you the report in plain English. And if the report raises questions, I'm around. That's kind of the whole point of CTF Designs, small business websites with this stuff handled.
