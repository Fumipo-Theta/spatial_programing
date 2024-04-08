# 空間を扱うプログラミング - チュートリアル -

## 環境セットアップ

1. asdf と asdf の python plugin をインストール
   * [asdf インストール](https://asdf-vm.com/guide/getting-started.html)
   * `asdf plugin add python`
2. python をインストール
   * `asdf install`
3. poetry をインストール ([公式ドキュメント](https://python-poetry.org/docs/#installing-with-the-official-installer))
   * `curl -sSL https://install.python-poetry.org | python -`
4. poetry (`$HOME/.local/bin/poetry`) へのパスを通す
   * zsh の場合
     * `echo 'export PATH=$HOME/.local/bin:$HOME' >> ~/.zshrc`
     * `source ~/.zshrc`
     * `poetry --version` (確認)
5. 仮想環境がリポジトリ内の `.venv/` に作られるようにする
   * `poetry config --local virtualenvs.in-project true`
6. `.tool-versions` に定義された python のバージョンを使って仮想環境をアクティベート
   * `poetry env use "$(cat ./.tool-versions | grep "python" | cut -d " " -f 2)"`
   * asdf で複数の python をインストールしている場合でも期待したバージョンが使われるようにするため
7. リポジトリの依存パッケージをインストール
   * `poetry install`

## テキストブック (Jupyter notebook) の起動

1. `poetry run jupyter lab`
2. Web ブラウザで [http://localhost:8888/lab](http://localhost:8888/lab) にアクセス
3. `1_coordinate_system.ipynb` を開く

## コントリビューター向け情報

### camera モデルの作成

1. ツールセットアップ
   * [MeshLab](https://www.meshlab.net/) を使用するので最新版をインストール
2. PLY (頂点ごとに色を持つ) と GLTF (mesh) 形式でモデルを出力
   * `poetry run python scripts/create_camera_obj.py ply`
   * `poetry run python scripts/create_camera_obj.py gltf`
   * 生成したモデルは [`data`](data/) ディレクトリに出力される
3. 生成した `PLY` と `GLTF` モデルの両方を MeshLab にインポートする
4. MeshLab でメッシュテクスチャを生成
   * `GLTF` モデルを選択
     * ツールバーの `Filter` > `Texture` > `Parameterization: Trivial Per-Triangle` を選択
     * ポップアップウィンドウ上の設定はデフォルトのまま `Apply`
   * ツールバーの `Filter` > `Texture` > `Transfer: Vertex Attribute to Texture (1 or 2 meshes)` を選択
     * `Source Mesh` を `PLY` モデルとする
     * `Target Mesh` を `GLTF` モデルとする
   * 結果として `GLTF` モデルに `PNG` 形式のテクスチャが紐づく
5. モデルを `OBJ` 形式でエクスポートする
   * ツールバーの `File` > `Export Mesh as` を選択
   * ファイルフォーマットを `Alias Wavefront Object (OBJ)` とする
   * 結果として下記のファイル群が生成される
     * メッシュマテリアルの `.obj` ファイル
     * マテリアルに関する `.mtl` ファイル
     * テクスチャの `.png` ファイル

* 上記で生成したカメラの OBJ モデルは、Unity asset としてインポート可能
  * 下記のような見た目になる
    ![Unityにインポートしたカメラモデル](./doc_images/unity_imported_camera_obj.png)
