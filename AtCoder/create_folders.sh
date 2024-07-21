#!/bin/bash

# ABC212からABC400までのフォルダを生成
for contest in $(seq 212 400); do
  abc_folder="ABC${contest}"
  mkdir -p "$abc_folder"

  # AからGまでのフォルダを生成
  for letter in {A..G}; do
    sub_folder="${abc_folder}/${letter}"
    mkdir -p "$sub_folder"

    # 各サブフォルダにanswer.py、myanswer.py、modularizationフォルダを生成
    echo "# This is the answer.py for problem ${letter} in ABC${contest}" > "${sub_folder}/answer.py"
    echo "# This is the myanswer.py for problem ${letter} in ABC${contest}" > "${sub_folder}/myanswer.py"
    mkdir -p "${sub_folder}/modularization"
    
    # modularizationフォルダにmain.pyを生成
    echo "#!/usr/bin/env python3" > "${sub_folder}/modularization/main.py"
    echo "# This is the main.py for problem ${letter} in ABC${contest}" >> "${sub_folder}/modularization/main.py"
    echo "def main():" >> "${sub_folder}/modularization/main.py"
    echo "    pass  # Add your solution logic here" >> "${sub_folder}/modularization/main.py"
    echo "" >> "${sub_folder}/modularization/main.py"
    echo "if __name__ == '__main__':" >> "${sub_folder}/modularization/main.py"
    echo "    main()" >> "${sub_folder}/modularization/main.py"
  done
done

echo "フォルダ構造の作成が完了しました。"
