// ==UserScript==
// @name          shorten djangoproject titles  0.2.0
// @namespace     http://wamber.net/
// @description   Shorten the page titles for Django documentation to be more tab friendly
// @include       http://www.djangoproject.com/*
// @include       http://code.djangoproject.com/*
// @include       http://djangoproject.com/*
// @include       http://docs.djangoproject.com/*
// ==/UserScript==
//
// William McVey
// 31 October, 2006

var doc_prefix = "/en/dev/"
var generic_django_prefix = "Django | "
var path = location.pathname
if (location.pathname == doc_prefix) {
	document.title = "doc index"
} else if (path.substr(0, doc_prefix.length) == doc_prefix) {
	// URL basename is good enough for the docs
	if (path.charAt(path.length - 1) == "/") {
		path = path.substr(0, path.length-1)
	}
	document.title = path.substr(doc_prefix.length) + " doc"
} else if (document.title.substr(0, generic_django_prefix.length)) {
	// Strip "Django | " from the default title
	document.title = document.title.substr(generic_django_prefix.length)
}
