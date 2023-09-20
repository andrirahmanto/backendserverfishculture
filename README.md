# :beginner: Backend Aqua Breeding

Web Service dalam bentuk REST Api untuk Backend Aqua Breeding

## :zap: Cara Menjalankan

1. Pastikan komputer/server sudah terinstall Python 3.6+ dan MongoDB
2. Install library python yang diperlukan
   - Flask
   - Flask-restful
   - Flask-mongoengine
5. Jalankan program salah satunya dengan menggunakan perintah `bash init-flash.sh`


## :wrench: Dokumentasi API

<details>
<summary><b>[GET]</b> Get Similarity Overall Ranking</summary>

- **URL**: `/api/v1.0/overall_ranking/similarity?keyword=barcelona&sort=similarity&start=0&length=10`
