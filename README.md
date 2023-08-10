# ASSISTANT IA POUR STREAMER

### Pour du divertissement

![alt text](https://raw.githubusercontent.com/anisayari/AIAssitantStreamer/main/assets/topic.png)

@TODO CONTRIBUTORS :list

- Screen des étapes,
- Rendre plus efficace le code (réduire la latence),
- Rajouter du langchain (si nécessaire et testant la latence) pour modifier son LLM, etc.
- Améliorer le README,
- etc.

## Configuration nécessaire

1. Exécutez `pip install -r requirements.txt` pour installer toutes les dépendances.

2. Remplissez le fichier `.env.example` avec vos clés API pour OPENAI, ELEVENLABS, et PICOVOICE. Renommez ce fichier
   en `.env`.

## Comment obtenir ces clés API

### Créez un compte sur OPENAI

1. Allez sur [OpenAI](https://www.openai.com/).
2. Inscrivez-vous pour un compte.
3. Une fois connecté, vous trouverez votre clé API dans le tableau de bord.

### Créez un compte sur ELEVENLABS

1. Allez sur [ElevenLabs](https://beta.elevenlabs.io/).
2. Inscrivez-vous pour un compte.
3. Une fois connecté, vous trouverez votre clé API dans le tableau de bord.

## Créez le mot clé (Wake Word) dans PICOVOICE

1. Allez sur [Picovoice Console](https://console.picovoice.ai/).
2. Créez un nouveau mot clé (Wake Word).
3. Téléchargez les fichiers nécessaires et ajoutez-les à votre projet.

## Comment générer les voix d'introduction sur Eleven

1. Connectez-vous à votre compte ElevenLabs.
2. Utilisez la fonctionnalité de génération de voix pour créer des voix d'introduction personnalisées.
3. Téléchargez ces voix et ajoutez-les manuellement à votre dossier 'voix_intro'.

## Annexes

### Erreur lors de l'installation de pyaudio

#### Debian 11 & 12

* `apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0`
* `pip install -r requirements.txt`

#### Macos

* `xcode-select --install`
* `brew install portaudio`
* `pip install -r requirements.txt`
