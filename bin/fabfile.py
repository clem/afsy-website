#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import re

from time import strftime
from fabric.api import *
from fabric.contrib.files import exists

adventcalendarpath = os.path.abspath(os.path.dirname(__file__) + '/../../afsy-calendrier-avent')
afsyfrpath = os.path.abspath(os.path.dirname(__file__) + '/../')


article_header = """{% extends 'AfsyFrontBundle:Avent:day.html.twig' %}

{% set year = 2013 %}

{% block article_title "Jour 17 - Commencer à adopter Devops sur ses projets Symfony" %}

{% block article_content %}

{% verbatim %}
"""


article_footer = """
{% endverbatim %}

{% endblock %}"""

article_bio = """
{% block article_avatar %}
    <img src="{{ asset('bundles/afsyfront/images/avent/17-fabrice.png') }} alt="Avatar Fabrice" />
{% endblock %}
{% block article_bio %}
<h2>
    <a href="{% block author_url %}http://www.theodo.fr{% endblock %}">{% block article_author %}Fabrice Bernhard{% endblock %}</a>
</h2>
<p>
   <a href="http://twitter.com/theodo">Fabrice</a> est co-fondateur et directeur technique de
   <a href="http://www.theodo.fr">Theodo</a>, une équipe de développement agile spécialisée sur Symfony2 et Node.js.
   Il est aussi en parallèle le directeur technique d'<a href="http://www.allomatch.com">Allomatch</a>,
   le moteur de recherche des matchs diffusés dans les bars.
   Cette double-casquette a permis d'acquérir une expérience unique dans la maintenance et l'évolution d'applications
   PHP à grande échelle, qui a été clef dans la découverte du mouvement Devops dès 2010.
</p>

{% endblock %}
"""

def adventcopy(daynum):

    with lcd(adventcalendarpath):
        local('./bin/console afsy:calendar')
        htmlfilename = glob.glob(adventcalendarpath + '/build/' + daynum + '*')[0]
        with open (htmlfilename, "r") as htmlfile:
            htmldata = htmlfile.read()

        m = re.search('<article>(.+?)</article>', htmldata, re.DOTALL)
        if m:
            htmldata = m.group(1)

        local('rsync -rav img/' + daynum + '-* ' + afsyfrpath + '/src/Afsy/Bundle/FrontBundle/Resources/public/images/avent/ ')
        local('rsync -rav img/' + daynum + '-* ' + afsyfrpath + '/src/Afsy/Bundle/FrontBundle/Resources/public/images/avent/ ')

    with lcd(afsyfrpath):
        with open('src/Afsy/Bundle/FrontBundle/Resources/views/Avent/day_2013_' + daynum + '.html.twig', 'w') as template:
            template.write(article_header)
            template.write(htmldata)
            template.write(article_footer)
            template.write(article_bio)






path = {
    'prod': '/theodo/v3.theodo.fr',
    'preprod': '/theodo/preprod.theodo.fr'
}

def theodo(command):
    return sudo(command, user='theodo')

@roles('preprod')
def checkout_project(tag):
    with cd(path[_getrole()]):
        if not exists(path[_getrole()] + '/.git', use_sudo=True):
            theodo('git clone --recursive git@github.com:theodo/theodo-fr.git .')

        theodo('git fetch')
        theodo('git fetch origin --tags')
        theodo('git checkout ' + tag)

@roles('preprod')
def deploy():
    tag = "%s/%s" % (_getrole(), strftime("%Y/%m-%d-%H-%M-%S"))
    local('git tag -a %s -m "%s"' % (tag, _getrole()))
    local('git push --tags')
    checkout_project(tag)

def _getrole():
    for role in env.roledefs:
        if env.host_string in env.roledefs[role]:
            return role

    raise Exception('Role not found')