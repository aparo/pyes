=================
Snowball Analyzer
=================

An analyzer of type **snowball** that uses the :doc:`standard tokenizer <./standard-tokenizer.html>`,  with :doc:`standard filter <./standard-tokenfilter.html>`,  :doc:`lowercase filter <./lowercase-tokenfilter.html>`,  :doc:`stop filter <./stop-tokenfilter.html>`,  and :doc:`snowball filter <./snowball-tokenfilter.html>`.  

The Snowball Analyzer is a stemming analyzer from Lucene that is originally based on the snowball project from `snowball.tartarus.org <http://snowball.tartarus.org>`_.  

Sample usage: 


.. code-block:: js

    {
        "index" : {
            "analysis" : {
                "analyzer" : {
                    "my_analyzer" : {
                        "type" : "snowball",
                        "language" : "English"
                    }
                }
            }
        }
    }


The **language** parameter can have the same values as the :doc:`snowball filter <./snowball-tokenfilter.html>`  and defaults to **English**. Note that only the languages English, Dutch, German, German2 and French have a default set of stopwords provided. 


The **stopwords** parameter can be used to provide stopwords for the languages that has no defaults, or to simply replace the default set with your custom list. A default set of stopwords for many of these languages is available from for instance `here <http://svn.apache.org/repos/asf/lucene/dev/branches/branch_3x/lucene/contrib/analyzers/common/src/resources/org/apache/lucene/analysis>`_  and `here. <http://svn.apache.org/repos/asf/lucene/dev/branches/branch_3x/lucene/contrib/analyzers/common/src/resources/org/apache/lucene/analysis/snowball>`_  

A sample configuration (in YAML format) specifying Swedish with stopwords:


.. code-block:: js

    index :
        analysis :
            analyzer : 
               my_analyzer: 
                    type: snowball
                    language: Swedish
                    stopwords: [och,det,att,i,en,jag,hon,som,han,på,den,med,var,sig,för,så,till,är,men,ett,om,hade,
                    de,av,icke,mig,du,henne,då,sin,nu,har,inte,hans,honom,skulle,hennes,där,min,man,ej,vid,kunde,
                    något,från,ut,när,efter,upp,vi,dem,vara,vad,över,än,dig,kan,sina,här,ha,mot,alla,under,någon,allt,
                    mycket,sedan,ju,denna,själv,detta,åt,utan,varit,hur,ingen,mitt,ni,bli,blev,oss,din,dessa,några,
                    deras,blir,mina,samma,vilken,er,sådan,vår,blivit,dess,inom,mellan,sådant,varför,varje,vilka,ditt,
                    vem,vilket,sitta,sådana,vart,dina,vars,vårt,våra,ert,era,vilkas]




