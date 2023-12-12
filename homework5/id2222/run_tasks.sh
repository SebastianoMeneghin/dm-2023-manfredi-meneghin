#!/bin/bash

# variables which will go inside for-loops
graphs="3elt add20 facebook"
node_policies="LOCAL HYBRID"
delta_exps="0.8 0.9"
delta_decays="1 2.5"
# best delta values found per annealing policy
delta_linear="0.005"
delta_exp="0.9"

function create_plot() {
  # find the most recently created output file
  output_file=$(ls --sort=time output/ | head -1)
  bash plot.sh output/$output_file $1
}

# clean the output directory and output images
mkdir -p images
rm -f output/*.txt images/*.png

for graph in $graphs; do
  # task 1
  for node_policy in $node_policies; do
    bash run.sh -graph ./graphs/${graph}.graph -delta $delta_linear -nodeSelectionPolicy $node_policy
    create_plot images/task1_${graph}_linear_d${delta_linear}_${node_policy,,}.png
  done

  # task 2.1
  for delta in $delta_exps; do
    bash run.sh -graph ./graphs/${graph}.graph -delta $delta -annealingSelectionPolicy EXPONENTIAL
    create_plot images/task21_${graph}_exp_d${delta}.png
  done

  # task 2.2
  bash run.sh -graph ./graphs/${graph}.graph -delta $delta_linear -annealingSelectionPolicy LINEAR -restart-temp
  create_plot images/task22_${graph}_linear_d${delta_linear}.png
  bash run.sh -graph ./graphs/${graph}.graph -delta $delta_exp -annealingSelectionPolicy EXPONENTIAL -restart-temp
  create_plot images/task22_${graph}_exp_d${delta_exp}.png

  # task 3
  for delta_decay in $delta_decays; do
    bash run.sh -graph ./graphs/${graph}.graph -delta $delta_exp -annealingSelectionPolicy IMPROVED_EXP -restart-temp -delta-decay $delta_decay
    create_plot images/task3_${graph}_impr_exp_d${delta_exp}_dd${delta_decay}.png
  done
done

echo "Creating table of results for Task 1"
python create_table.py --graphs $graphs --annealing-policy LINEAR --delta $delta_linear --node-policy $node_policies > task1.tex

echo "Creating table of results for Task 2.1"
python create_table.py --graphs $graphs --annealing-policy EXPONENTIAL --delta $delta_exps > task21.tex

echo "Creating table of results for Task 2.2"
python create_table.py --graphs $graphs --annealing-policy LINEAR EXPONENTIAL --delta $delta_linear $delta_exp --restart-temp > task22.tex

echo "Creating table of results for Task 3"
python create_table.py --graphs $graphs --annealing-policy IMPROVED_EXP --delta $delta_exp --delta-decay $delta_decays --restart-temp > task3.tex