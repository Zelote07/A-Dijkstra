# Guide de rédaction du mini-mémoire
## Algorithmique et ingénierie de données – M1

## Ce que ce mémoire n'est pas

Ce mémoire n'est pas un rapport de stage, ni un résumé de cours, ni une liste de définitions. Ce n’est pas non plus une thèse. Voyez-le plutôt comme un exposé, plus professionnel et plus approfondi. C'est un **mini-cours que vous rédigez pour vos camarades** : vous avez compris quelque chose en profondeur, et vous l'expliquez à quelqu'un qui ne le connaît pas encore. Gardez cette image en tête à chaque paragraphe que vous écrivez. Si vous vous retrouvez à recopier une définition Wikipedia sans l'expliquer avec vos propres mots, c'est que vous êtes à côté de la plaque.

N’oubliez pas :

> *Avant donc que d'écrire, apprenez à penser.
> Selon que notre idée est plus ou moins obscure,
> L'expression la suit, ou moins nette, ou plus pure.
> Ce que l'on conçoit bien s'énonce clairement,
> Et les mots pour le dire arrivent aisément.
> À découvrir sur le site*
> (Boileau, [Chant 1 de l’Art poétique](https://www.poesie-francaise.fr/nicolas-boileau/poeme-l-art-poetique-chant-I.php))

## 1. Construire le plan

### La logique générale : du problème à la solution

Un bon mémoire part d'une **situation concrète** et d'un **problème réel**, présente les **outils théoriques** qui permettent de le résoudre, montre une **implémentation** qui prouve que la solution fonctionne, et analyse honnêtement les **limites** de cette solution. Ce n'est pas une structure arbitraire : c'est la structure naturelle de toute démarche d'ingénierie, de recherche, etc.,  avec laquelle vous devez commencer à être familiers.

### Plan générique suggéré

**Rappel du format** :

- interligne 1,5
- police taille 12 (pour du Times New Roman)
- 12 pages (± 15%)
- marges 2,5cm
- à titre indicatif une page standard contient en moyenne 2 000 à 2 500 caractères ou 350 mots (en moyenne)
- n’oubliez pas qu’une bonne illustration (figure) vaut mille mots !

**Introduction (1 à 1,5 page)**

On a dû vous le répéter mille fois depuis que vous écrivez des trucs à l’école : c'est la partie la plus importante et celle qu'on écrit en dernier. Elle doit répondre à trois questions dans l'ordre : Quel est le problème concret que vous traitez ? Pourquoi ce problème est-il difficile ou intéressant ? Quelle est votre approche pour y répondre ?

L'introduction se termine par une **problématique** formulée en une ou deux phrases précises. Pas « Nous allons étudier les tables de hachage », mais plutôt « Comment garantir un accès en temps constant à des données dans un référentiel de millions d'entrées, et quelles sont les conditions pour que cette garantie tienne ? »

**Contexte et motivation (0,5 à 1 page)**

Montrez pourquoi le problème est important dans le contexte de la data science ou du data engineering. C’est le moment de dérouler des exemples concrets, de donner des ordres de grandeur, éventuellement une comparaison avec l'approche naïve qui ne passe pas à l'échelle (en général c’est ce que je vous demande d’implémenter en première intention). C'est ici que vous donnez au lecteur une raison de continuer à lire.

**Fondements théoriques (2 à 3 pages)**

La partie la plus dense. Présentez les concepts clés dans un ordre pédagogique et pas dans l'ordre dans lequel vous les avez découverts. Chaque concept doit être introduit par un exemple ou une intuition avant d'être formalisé. Les formules et les notations de complexité ont leur place ici, mais elles doivent être expliquées, pas posées.

Ne cherchez pas à être exhaustif. Un concept bien expliqué vaut mieux que cinq concepts survolés. Sélectionnez ce qui est strictement nécessaire pour comprendre votre implémentation. Je ne vous demande pas des preuves formelles, des démonstrations en détail, donnez nous l’intuition, les clefs pour comprendre. Inspirez vous des chaînes de vulgarisation (comme 3blue1brown). 

**Implémentation (2 à 3 pages)**

Présentez votre code de façon sélective, pas ligne par ligne, mais en expliquant les choix importants (a priori on sait tous coder). En gros, expliquer un bout de code pour lequel vous écririez un commentaire. Pour chaque fonction ou classe, expliquez ce qu'elle fait, pourquoi elle est conçue ainsi, et quels cas limites elle gère. Les listings de code complets vont en annexe ; ici, vous montrez des extraits commentés des parties les plus significatives. Si vous tenez à développer un concept, une théorie, etc. et que ça alourdit trop votre texte principal : faites vous plaisir en annexe, et préservez votre discours qui doit rester intelligible et digeste.

Incluez des mesures de performance : temps d'exécution, consommation mémoire, comparaisons avec des alternatives. Encore une fois un graphique vaut souvent mieux qu'un tableau de chiffres (il paraît que vous avez eu des cours de dataviz ?).

**Application et résultats (1 à 2 pages)**

Décrivez rapidement votre dataset synthétique : comment vous l'avez construit, pourquoi il est adapté à votre sujet, quels cas limites il contient. Inutile d’aller dans les détails non plus (vous disposer d’une annexe pour ca). Présentez les résultats de votre démo avec des captures d'écran ou des graphiques. Et surtout, commentez les résultats, même si ça vous semble évident. Vous vous aviez la tête dans le guidon. Ce n’est pas forcément le cas du lecteur. Ce n’est pas au lecteur de faire l’effort de comprendre ce que vos résultats veulent dire, s’ils vont dans votre sens ou pas, ne croyez pas qu’un résultat parle de lui-même. Économisez l’énergie cognitive du lecteur (n’oubliez pas que j’aurai 10 mémoires à lire…) et mâchez-lui le travail ! N’hésitez pas à reprendre les éléments de votre question de départ (vu que c’est la questions à laquelle vous essayez de répondre).

**Discussion et limites (1 page)**

Scoop : c’est ici que je vais comprendre si vous maîtrisez votre sujet. Quand est-ce que votre algorithme ne fonctionne plus bien ? Quelles hypothèses doit-on vérifier pour que les performances annoncées soient effectives ? Quelles seraient les prochaines étapes si ce travail devait continuer ? Un étudiant qui identifie honnêtement les limites de ce qu'il présente montre qu'il a compris en profondeur.

**Conclusion (0,5 page)**

Répondez à votre problématique en une ou deux phrases. Résumez les apports de votre travail. Éventuellement, une ouverture sur ce que vous n'avez pas traité.

**Bibliographie**

Voir la section dédiée ci-dessous.

**Annexes**

- Code source complet (ou lien vers le dépôt Git)
- Tableaux de données bruts ou comment vous avez généré vos données (ce sera ce dernier cas ici), et bien sûr quelque stats descriptives peuvent ne pas faire de mal si elles sont pertinentes, pour se faire une idée de la tête des données sur lesquelles vous avez travaillé (à adapter en fonction du type de données) et ne serait-ce que vérifier qu’elles répondent aux critères que vous avez défini.
- Démonstrations mathématiques détaillées si pertinent (et si ça vous a passionné)
- Captures d'écran supplémentaires de la démo

### Ce qui va en annexe et ce qui reste dans le corps

La règle est simple : si supprimer ce contenu empêche de comprendre le mémoire, il reste dans le corps. Si c'est une référence utile mais pas indispensable à la lecture, ça va en annexe. Du code trop long va presque toujours en annexe. Personne ne lit 200 lignes de code dans un mémoire. Les extraits commentés des parties clés, eux, restent dans le corps.

## 2. Utiliser l'IA efficacement

L'IA est un outil puissant pour vous aider dans ce type de travail et je ne me fais aucune illusion : la plupart d’entre vous l’utilisera. Mon approche est donc celle de « réduction des risques ». Je vous laisse le droit de l’utiliser, à condition de rester maître de vos usages, de savoir ce que vous lui demander et de ne pas lui déléguer ce qui doit rester votre travail de compréhension.

### L’IA est utile pour :

**Comprendre un concept difficile**

C'est probablement l'usage le plus précieux. Quand un article ou un cours explique quelque chose de façon trop abstraite, demandez à l'IA de vous l'expliquer autrement, avec un exemple différent, avec une métaphore, ou en supposant que vous n'avez jamais vu le concept. Par exemple :

> "Explique-moi le facteur d'équilibre dans un arbre AVL comme si j'avais compris les arbres binaires mais pas encore les rotations. Donne-moi un exemple avec 5 insertions."

Comparez ensuite l'explication de l'IA avec votre source originale. Si elles sont cohérentes, vous avez très probablement compris. Si elles diffèrent, creusez la divergence, c'est souvent là que se cache la petite bête.

Attentions aux « hallucinations » !!!! Croisez les sources. Vérifiez. Demandez toujours les sources.

Parfois l’IA vous recrachera à quelques mots près ce qu’on trouve dans Wikipédia (normal : c’est sur ça qu’elle a été entraîné). Quel valeur ajoutée dans ce cas ? Prenez du recul, et utilisez systématiquement d’autres sources (Wikipedia, articles de blogs, articles, livres, tuto ou vulgarisation sur youtube, MOOC…)

Si l’IA vous fait aller 5 fois plus vite, c’est que vous l’utilisez mal. On peut estimer que le gain réel – si vous faites bien les vérifications nécessaires, si vous relisez bien et essayez de comprendre, et c’est ce qui prend le plus de temps – est plutôt de 20%… 

**Comprendre un article ou une documentation technique**

Collez dans le prompt un extrait d'article ou de documentation et demandez : « Qu'est-ce que ce passage veut dire concrètement ? Y a-t-il des hypothèses implicites que l'auteur ne formule pas explicitement ? » L'IA peut-être intéressante pour détecter les raccourcis que font les auteurs d'articles techniques quand ils supposent que le lecteur connaît déjà certaines choses et vous diriger vers les sources complémentaires.

**Constituer une première webographie**

Demandez à l'IA de vous orienter vers des ressources pour un sujet donné. Elle ne peut pas vous donner des liens garantis valides (ses connaissances ont une date de coupure), mais elle peut vous indiquer des noms d'auteurs, des noms d'algorithmes connexes, des noms de papiers de référence que vous rechercherez vous-même. Par exemple :

> "Quels sont les articles fondateurs sur HNSW ? Qui sont les auteurs principaux de cette littérature ?"

Vérifiez **toujours** l'existence et le contenu réel des sources que l'IA mentionne, elle peut halluciner des titres ou des auteurs !!!

**Déboguer du code**

Collez votre code et l'erreur obtenue. L'IA est très efficace pour identifier des erreurs de logique, des cas limites oubliés, ou des problèmes de performance. Mais lisez et comprenez la correction proposée avant de l'appliquer, un bug non compris est un bug susceptible de faire « bugguer » votre l'oral.

**S'auto-tester**

Demandez à l'IA de vous poser des questions sur ce que vous venez d'apprendre. Par exemple :

> "Je viens d'implémenter Dijkstra avec un min-heap. Pose-moi 5 questions pour vérifier que j'ai vraiment compris – pas des questions factuelles, mais des questions qui testent la compréhension."

Si vous ne savez pas répondre à certaines questions, vous avez identifié exactement ce qu'il vous reste à travailler. C'est une façon très efficace de préparer les 5 minutes de questions à l'oral.

C’est un résultat robuste de la psychologie cognitive. On retient d’autant mieux une information qu’on l’a traitée en profondeur. Relire un cours n’est pas très efficace. Créer des fiches de lectures (ce qui vous force à reformuler) est un peu plus efficace, mais pas beaucoup. Les meilleurs résultats sont obtenu avec l’auto-test (où là on est obliger de retrouver une info en mémoire ce qui à force de répétitions approfondie sa trace mnésique) et surtout quand on apprend ce qu’on est sensé savoir à quelqu’un d’autre : cela nous obliger expliquer, reformuler, retrouver de l’information en mémoire, etc. ce qui est le sommet du traitement en profondeur. C’est d’ailleurs pour cela que je vous fais faire un mémoire et sa présentation orale !

Utiliser l’IA pour cela : demandez-lui de vous poser des questions, p. ex. un quizz (en lui indiquant de ne pas vous donner les réponses tout de suite), demandez-lui de juger si vos explications sont solides, etc.

**Structurer vos idées**

Quand vous avez des notes en vrac et que vous cherchez à les organiser, l'IA peut vous aider à identifier les grands blocs thématiques et leur ordre logique. Donnez-lui vos notes brutes et demandez : « Comment organiserais-tu ces idées en sections pour un mémoire de 10 pages ? » **Attention**, utilisez ce plan comme point de départ, pas comme version finale.

Vous pouvez lui demander aussi si vous avez « raté » un point théorique important.

### Ce que l'IA ne doit pas faire à votre place

**Écrire vos paragraphes de fond**

Vous pouvez demander à l'IA de reformuler un paragraphe que vous avez écrit pour qu'il soit plus clair, ou de vérifier si votre explication est correcte. Vous ne devez pas lui demander d'écrire la section « Fondements théoriques » et la copier telle quelle. La raison est simple et pragmatique : à l'oral, vous devrez expliquer avec vos propres mots ce qui est dans votre mémoire. Un texte que vous n'avez pas produit sera impossible à défendre sous pression.

Et même si vous faites illusion, vous aurez peut-être la satisfaction d’avoir été plus malin que le prof ou vos camarades, mais en fin de compte ça ne vous aura rien apporté et surtout vous resterez dépendant de l’IA. Acquérir une connaissance, un diplôme devrait vous rentre plus autonome, et là c’est l’inverse qui va se produire… à vous de voir.

**Valider vos résultats expérimentaux**

L'IA ne peut pas exécuter votre code, mesurer vos temps d'exécution ni vérifier que vos graphiques sont corrects. Ces parties doivent venir de vous. Mais l’IA peut vous aider à trouver comment faire vos tests.

**Remplacer la lecture des sources**

L'IA peut vous aider à comprendre un article, mais elle ne remplace pas sa lecture. Les nuances, les hypothèses, les limites que les auteurs eux-mêmes formulent c’est à vous de les détecter dans l’article, et ça ne figurera pas nécessairement dans le résumé de l'IA. « Le diable est dans les détails » dit-on.

### La règle d'or

Après chaque interaction avec l'IA, posez-vous la question : « Est-ce que je pourrais expliquer ce que je viens d'apprendre à un camarade, sans l'aide de l'IA, avec mes propres mots ? » 

Si la réponse est non, vous n'avez pas encore vraiment appris : vous avez juste lu et vous aurez oublié d’ici la fin de la journée.

## 3. Trier l'information

Vous allez être confrontés à des sujet dont, j’espère – car c’est le but –, vous ne savez rien pour le moment. Dans un premier temps notez les concepts ou les mots de vocabulaires qui sont inconnus. Faites des recherches, notez ce qu’ils veulent dire, ce à quoi ils se rapportent, comment ils sont liés entre eux.

Quand on travaille sur un sujet algorithmique pour la première fois, on est rapidement submergé : articles Wikipedia, papiers de recherche, tutoriels YouTube, billets de blog, documentation officielle, Stack Overflow, cours universitaires en ligne. Tout semble important. Rien n'est hiérarchisé.

### Construire une carte mentale des sources

Avant de commencer à lire sérieusement, passez une heure à recenser les ressources disponibles sans les lire en profondeur. Notez pour chaque source : de quel type elle est (tutoriel, article académique, documentation, blog), à qui elle s'adresse (débutant, praticien, chercheur), et ce qu'elle couvre en une phrase. À l'issue de cette heure, vous aurez une vision d'ensemble et vous pourrez choisir votre parcours de lecture plutôt que de vous laisser emporter par la première source venue. On tombe vite dans un « rabbit hole ».

### La hiérarchie des sources

Toutes les sources n'ont pas la même valeur. Dans l'ordre décroissant de fiabilité pour un mémoire académique :

**Articles de recherche originaux** : c'est là que les algorithmes ont été publiés pour la première fois. Ils sont rigoureux mais souvent difficiles. Lisez au moins l'abstract, l'introduction et la conclusion de l'article original de votre algorithme principal. Citez au moins l’article princeps.

**Documentation officielle des bibliothèques** : sklearn, numpy, networkx, faiss, pgvector. Précise, à jour, fiable.

**Cours universitaires en ligne** : Pédagogiques et rigoureux. Certains enseignants en université laissent des ressources en lignes sur leur page perso ou dépôts (slides, support de cours, etc.). Vous avez aussi des MOOC comme : MIT OpenCourseWare, Stanford CS, FUN. Hélas souvent les MOOC ne sont disponibles que pour une durée donnée, il faut s’inscrire.  Certains cours en lignes ont leurs propre chaîne youtube (c’est le cas pour CS).

**Livres de référence** : Introduction to Algorithms (CLRS), The Algorithm Design Manual, etc. Lents à lire mais très fiables. Il faut pouvoir y accéder…

**Billets de blog techniques de qualité** – distill.pub, Towards Data Science (avec discernement), Medium (idem), blogs d'ingénierie de grandes entreprises (Google AI, Meta Engineering). Utiles pour les intuitions et les exemples pratiques.

**Wikipedia** : bon point d'entrée pour s'orienter, à ne jamais citer comme source principale.

**Tutoriels aléatoires** : utiles pour le code, à vérifier avec les sources primaires pour la théorie.

### La règle des trois sources

C’est plutôt une règle journalistique, mais elle fait bien passer l’idée que plus on a de sources / résultats qui vont dans le même sens (pourvu que ces sources soient indépendantes !!!), plus on peut avoir confiance dans la robustesse du résultat. Pour chaque affirmation importante que vous faites dans votre mémoire – une complexité, une propriété d'un algorithme, une comparaison de performances – vérifiez qu'au moins deux sources indépendantes sont d'accord. Si vous ne trouvez qu'une source pour une affirmation, signalez-le avec une formulation prudente ("selon X…") plutôt que de l'affirmer comme une vérité universelle.

Mais honnêtement pour un mini-mémoire comme celui-ci inutile de prendre trop de précautions oratoires, notamment parce que vous travaillerez sur des résultats bien éprouvés (mais faites le pour vous !)

### Savoir quand arrêter de chercher

Il y a un moment où lire davantage ne vous apprend plus grand chose de nouveau : vous retombez sur les mêmes idées reformulées. C'est le signal que vous en savez assez pour commencer à écrire. Écrire est une façon d'apprendre : vous découvrirez les trous dans votre compréhension en essayant de formuler des phrases claires (rappelez vous de Boileau).

## 4. Constituer la bibliographie

### Ce qu'une bibliographie doit contenir

Pour un mémoire de ce type, visez entre 6 et 12 références. L'objectif n'est pas d'en avoir beaucoup, mais d'en avoir des pertinentes et de montrer que vous savez distinguer les sources primaires des sources secondaires.

La bibliographie doit contenir au minimum :
- L'article ou le chapitre d'ouvrage qui a introduit l'algorithme principal que vous étudiez
- La documentation officielle de la ou des bibliothèques Python utilisées
- Un ou deux ouvrages de référence sur les structures de données ou les algorithmes
- Les ressources spécifiques que vous avez réellement utilisées pour comprendre des points difficiles

### Format de citation

Utilisez un format cohérent. Pour un mémoire technique, le format APA ou le format IEEE sont tous les deux acceptables. Ce qui compte, c'est la cohérence et le fait que chaque référence contienne les informations suffisantes pour que le lecteur puisse retrouver la source.

Pour un article académique : Auteur(s), Année, Titre, Nom de la conférence ou revue, DOI ou URL.

Pour un livre : Auteur(s), Année, Titre, Éditeur.

Pour une documentation en ligne : Nom de la bibliothèque ou du projet, Titre de la page, URL, Date d'accès.

### Citer l'IA

Si vous avez utilisé une IA pour comprendre un concept ou pour déboguer du code, mentionnez-le dans une section « Outils utilisés » séparée de la bibliographie. Indiquez quel outil, pour quoi faire, et comment vous avez vérifié les informations obtenues. Ce n'est pas obligatoire sur la forme, mais c'est la bonne pratique intellectuelle, et ça montre que vous avez réfléchi à votre usage de l'outil.

## 5. Recommandations pratiques

### Sur le processus d'écriture

**Écrivez tôt et mal.** La page blanche est votre pire ennemi. Commencez par écrire une version brouillon sans vous préoccuper du style. Vous ne pouvez pas améliorer ce qui n'existe pas encore. Une phrase maladroite mais présente est infiniment plus utile qu'une phrase parfaite que vous n'avez pas encore écrite (et que donc, vous ne pourrez jamais corriger).

>*Hâtez-vous lentement, et, sans perdre courage,
>Vingt fois sur le métier remettez votre ouvrage
>Polissez-le sans cesse et le repolissez ;
>Ajoutez quelquefois, et souvent effacez.*
>
>Boileau, toujours…

**Séparez la recherche de l'écriture.** Quand vous êtes en mode "recherche", prenez des notes brutes sans chercher à formuler des phrases finales. Quand vous êtes en mode "écriture", fermez vos onglets de recherche et écrivez à partir de vos notes. Mélanger les deux ralentit les deux activités.

**Relisez à voix haute.** Si une phrase est difficile à lire à voix haute, c'est qu'elle est trop longue ou trop complexe. Découpez-la. Les phrases de plus de 40 mots dans un texte technique sont presque toujours un problème.

**Faites relire par quelqu'un d'autre**, idéalement quelqu'un qui ne connaît pas votre sujet. Si cette personne ne comprend pas un passage c'est que votre explication n’est pas au niveau.

### Sur la démo

**Testez votre démo la veille.** Pas le matin de la présentation. Les installations de bibliothèques, les conflits de dépendances, les ports qui ne s'ouvrent pas, tout ça prend du temps.

**Ayez un plan B.** Si Streamlit ne se lance pas le jour J, ayez des captures d'écran des résultats dans vos slides. Si votre notebook tourne trop lentement, ayez une version pré-exécutée avec les sorties visibles.

**Votre dataset synthétique doit être fixé.** Utilisez `random_state=42` ou équivalent partout. Les résultats que vous montrez dans le mémoire doivent être reproductibles de façon identique par n'importe qui qui exécute votre code.

### Sur la présentation orale

Vous avez déjà eu un cours sur la communication.

La présentation de 15 minutes suit naturellement la structure du mémoire, mais avec une contrainte : vous ne pouvez pas tout dire. Choisissez les deux ou trois idées les plus importantes et développez-les vraiment plutôt que de survoler tout le mémoire.

Les 5 minutes de questions sont souvent les plus révélatrices. Anticipez les questions difficiles en vous posant vous-mêmes les questions de la fiche de sujet (« Ce que vous devrez être capables d'expliquer à l'oral »). Si vous ne savez pas répondre à l'une d'elles, c'est un signal clair sur ce qu'il vous reste à travailler.

Une réponse honnête vaut mieux qu'une réponse improvisée. « Je ne suis pas sûr, mais je pense que… » suivi d'un raisonnement cohérent montre plus de compréhension que de sortir une formule mal mémorisée.

### Sur la gestion du temps

Deux semaines de préparation avant le début des cours, puis des créneaux « Mémoire » pendant les dix jours de cours : c'est peu. Voici une répartition réaliste.

**Semaines de préparation (avant les cours)**

Premier tiers : exploration du sujet, construction de la webographie, lectures de survol, premières expérimentations de code. À l'issue de cette phase, vous devez avoir un plan de mémoire validé.

Deuxième tiers : lectures approfondies des sources principales, implémentation des algorithmes, construction du dataset synthétique.

Dernier tiers : rédaction des sections Fondements théoriques et Implémentation. Ces sections sont les plus longues à écrire.

**Pendant les cours**

Les créneaux « mémoire », outre des échanges pour avancer sur l’implémentation et la compréhension théorique, servent à finaliser ce que vous n'avez pas eu le temps de terminer : section Application et résultats, Discussion et limites, Introduction et Conclusion (qui s'écrivent en dernier), mise en page, préparation des slides.

Ne laissez pas la rédaction entière pour les créneaux « mémoire » : vous n'aurez pas le temps.

## Checklist avant de rendre

Avant de déposer votre mémoire, vérifiez que :

- [ ] La problématique est formulée explicitement dans l'introduction
- [ ] Chaque concept théorique est introduit par un exemple ou une intuition avant d'être formalisé
- [ ] Les extraits de code dans le corps du mémoire sont commentés et expliqués (pas juste copiés)
- [ ] Vous avez mesuré et affiché les performances de votre implémentation
- [ ] Vous avez discuté au moins deux limites de votre approche
- [ ] La bibliographie contient l'article ou l'ouvrage original de votre algorithme principal
- [ ] Le dataset synthétique est reproductible (graine aléatoire fixée), les contraintes auxquelles il obéit sont spécifiées
- [ ] La démo fonctionne sur une machine autre que la vôtre
- [ ] Vous avez relu le mémoire à voix haute
- [ ] Vous êtes capables de répondre aux questions de la fiche de sujet sans consulter le mémoire
- [ ] Vous vous êtes testés mutuellement sur un quizz et les aspects principaux du mémoire