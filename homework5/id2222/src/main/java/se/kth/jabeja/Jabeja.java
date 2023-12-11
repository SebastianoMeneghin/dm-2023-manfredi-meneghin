package se.kth.jabeja;

import org.apache.log4j.Logger;
import se.kth.jabeja.config.Config;
import se.kth.jabeja.config.NodeSelectionPolicy;
import se.kth.jabeja.io.FileIO;
import se.kth.jabeja.rand.RandNoGenerator;
// Add import from Config class
import se.kth.jabeja.config.AnnealingSelectionPolicy;

import java.io.File;
import java.io.IOException;
import java.util.*;

public class Jabeja {
  final static Logger logger = Logger.getLogger(Jabeja.class);
  private final Config config;
  private final HashMap<Integer/*id*/, Node/*neighbors*/> entireGraph;
  private final List<Integer> nodeIds;
  private int numberOfSwaps;
  private int round;
  private float T;
  private boolean resultFileCreated = false;

  private Random random = new Random();
  private boolean linearAnnealing = false;

  // String to change output file path
  private String outputFilePath = null;

  // parameters for restarting the temperature
  private int sameEdgeCutRounds = 0;
  private int currentEdgeCut = 0;
  private int previousEdgeCut = 0;

  //-------------------------------------------------------------------
  public Jabeja(HashMap<Integer, Node> graph, Config config) {
    this.entireGraph = graph;
    this.nodeIds = new ArrayList(entireGraph.keySet());
    this.round = 0;
    this.numberOfSwaps = 0;
    this.config = config;
    this.T = config.getTemperature();

    this.random.setSeed(config.getSeed());
    this.linearAnnealing = config.getAnnealingPolicy() == AnnealingSelectionPolicy.LINEAR;

    if (!linearAnnealing)
      config.setTemperature(1.0f);
  }


  //-------------------------------------------------------------------
  public void startJabeja() throws IOException {
    for (round = 0; round < config.getRounds(); round++) {
      for (int id : entireGraph.keySet()) {
        sampleAndSwap(id);
      }

      //one cycle for all nodes have completed.
      //reduce the temperature
      saCoolDown();
      report();
      restartTemperature();
    }
  }

  /**
   * Simulated analealing cooling function
   */
  private void saCoolDown(){
    float min_temp = 0.0001f;
    if (linearAnnealing){ min_temp = 1.0f;}

    if (T > min_temp && linearAnnealing){
      // decrease temperature linearly over time
      T -= config.getDelta();
    } 
    else if (T > min_temp && !linearAnnealing){
      // decrease temperature exponentially over time
      T *= config.getDelta();
    } 
    else {
      T = min_temp;
    }
  }

  /**
   * Sample and swap algorith at node p
   * @param nodeId
   */
  private void sampleAndSwap(int nodeId) {
    Node partner = null;
    Node nodep = entireGraph.get(nodeId);

    if (config.getNodeSelectionPolicy() == NodeSelectionPolicy.HYBRID
            || config.getNodeSelectionPolicy() == NodeSelectionPolicy.LOCAL) {
      // swap with random neighbors
      partner = findPartner(nodeId, getNeighbors(nodep));
    }

    if (config.getNodeSelectionPolicy() == NodeSelectionPolicy.HYBRID
            || config.getNodeSelectionPolicy() == NodeSelectionPolicy.RANDOM) {
      // if local policy fails then randomly sample the entire graph
      if (partner == null)
        partner = findPartner(nodeId, getSample(nodeId));
    }

    // swap the colors
    if (partner != null) {
      int colorp = nodep.getColor();
      nodep.setColor(partner.getColor());
      partner.setColor(colorp);
      numberOfSwaps++;
    }
  }

  public Node findPartner(int nodeId, Integer[] nodes){

    Node nodep = entireGraph.get(nodeId);
    float alpha = config.getAlpha();

    Node bestPartner = null;
    double highestBenefit = 0;

    // find best node as swap partner for node p
    for (int node : nodes) {
      Node nodeq = entireGraph.get(node);

      // compute dpp and dqq
      int dpp = getDegree(nodep, nodep.getColor());
      int dqq = getDegree(nodeq, nodeq.getColor());
      double oldValue = Math.pow(dpp, alpha) + Math.pow(dqq, alpha);

      // compute dpq and dqp
      int dpq = getDegree(nodep, nodeq.getColor());
      int dqp = getDegree(nodeq, nodep.getColor());
      double newValue = Math.pow(dpq, alpha) + Math.pow(dqp, alpha);

      boolean updateSolution = false;
      double currentBenefit = 0, acceptanceProb = 0;

      if (linearAnnealing) {
        currentBenefit = newValue;
        updateSolution = newValue * T > oldValue;

      } else {  // exponential or improved exponential annealing policies
        if (config.getAnnealingPolicy() == AnnealingSelectionPolicy.EXPONENTIAL) {
          // acceptance probability: a_p = e^((new - old) / T)
          acceptanceProb = Math.exp((newValue - oldValue) / T);

        } else if (config.getAnnealingPolicy() == AnnealingSelectionPolicy.IMPROVED_EXP) {
          // acceptance probability: a_p = e^((1/old - 1/new) / T)
          acceptanceProb = Math.exp((1 / oldValue - 1 / newValue) / T);
        }
        
        currentBenefit = acceptanceProb;
        updateSolution = acceptanceProb > random.nextDouble() && newValue != oldValue;
      }

      // update the best partner and highest benefit
      if (currentBenefit > highestBenefit && updateSolution) {
        bestPartner = nodeq;
        highestBenefit = currentBenefit;
      }
    }

    return bestPartner;
  }

  /**
   * Restart temperature if edge cut has converged (may be a local minimum)
   */
  private void restartTemperature() {
    // only restart the temperature if that flag is set
    if (!config.getRestartTemp()) return;

    // check if the edge cut has remained constant between rounds
    if (currentEdgeCut == previousEdgeCut) {
      sameEdgeCutRounds++;

      if (sameEdgeCutRounds == config.getRoundsRestart()) {
        T = config.getTemperature();

        // decaying delta over time may converge to better solutions
        config.setDelta(config.getDelta() / (1+config.getDeltaDecay()));
        sameEdgeCutRounds = 0;
      }
    } else {
      sameEdgeCutRounds = 0;
    }
    // update to the current edge cut
    previousEdgeCut = currentEdgeCut;
  }


  /**
   * The the degreee on the node based on color
   * @param node
   * @param colorId
   * @return how many neighbors of the node have color == colorId
   */
  private int getDegree(Node node, int colorId){
    int degree = 0;
    for(int neighborId : node.getNeighbours()){
      Node neighbor = entireGraph.get(neighborId);
      if(neighbor.getColor() == colorId){
        degree++;
      }
    }
    return degree;
  }

  /**
   * Returns a uniformly random sample of the graph
   * @param currentNodeId
   * @return Returns a uniformly random sample of the graph
   */
  private Integer[] getSample(int currentNodeId) {
    int count = config.getUniformRandomSampleSize();
    int rndId;
    int size = entireGraph.size();
    ArrayList<Integer> rndIds = new ArrayList<Integer>();

    while (true) {
      rndId = nodeIds.get(RandNoGenerator.nextInt(size));
      if (rndId != currentNodeId && !rndIds.contains(rndId)) {
        rndIds.add(rndId);
        count--;
      }

      if (count == 0)
        break;
    }

    Integer[] ids = new Integer[rndIds.size()];
    return rndIds.toArray(ids);
  }

  /**
   * Get random neighbors. The number of random neighbors is controlled using
   * -closeByNeighbors command line argument which can be obtained from the config
   * using {@link Config#getRandomNeighborSampleSize()}
   * @param node
   * @return
   */
  private Integer[] getNeighbors(Node node) {
    ArrayList<Integer> list = node.getNeighbours();
    int count = config.getRandomNeighborSampleSize();
    int rndId;
    int index;
    int size = list.size();
    ArrayList<Integer> rndIds = new ArrayList<Integer>();

    if (size <= count)
      rndIds.addAll(list);
    else {
      while (true) {
        index = RandNoGenerator.nextInt(size);
        rndId = list.get(index);
        if (!rndIds.contains(rndId)) {
          rndIds.add(rndId);
          count--;
        }

        if (count == 0)
          break;
      }
    }

    Integer[] arr = new Integer[rndIds.size()];
    return rndIds.toArray(arr);
  }


  /**
   * Generate a report which is stored in a file in the output dir.
   *
   * @throws IOException
   */
  private void report() throws IOException {
    int grayLinks = 0;
    int migrations = 0; // number of nodes that have changed the initial color
    int size = entireGraph.size();

    for (int i : entireGraph.keySet()) {
      Node node = entireGraph.get(i);
      int nodeColor = node.getColor();
      ArrayList<Integer> nodeNeighbours = node.getNeighbours();

      if (nodeColor != node.getInitColor()) {
        migrations++;
      }

      if (nodeNeighbours != null) {
        for (int n : nodeNeighbours) {
          Node p = entireGraph.get(n);
          int pColor = p.getColor();

          if (nodeColor != pColor)
            grayLinks++;
        }
      }
    }

    int edgeCut = grayLinks / 2;

    logger.info("round: " + round +
            ", edge cut:" + edgeCut +
            ", swaps: " + numberOfSwaps +
            ", migrations: " + migrations);

    saveToFile(edgeCut, migrations);
  }

  private void saveToFile(int edgeCuts, int migrations) throws IOException {
    String delimiter = "\t\t";
    String outputFilePath;

    //output file name
    File inputFile = new File(config.getGraphFilePath());
    outputFilePath = config.getOutputDir() +
            File.separator +
            inputFile.getName() + "_" +
            "AP" + "_" + config.getAnnealingPolicy() + "_" +
            "NS" + "_" + config.getNodeSelectionPolicy() + "_" +
            "GICP" + "_" + config.getGraphInitialColorPolicy() + "_" +
            "T" + "_" + config.getTemperature() + "_" +
            "D" + "_" + config.getDelta() + "_" +
            "RNSS" + "_" + config.getRandomNeighborSampleSize() + "_" +
            "URSS" + "_" + config.getUniformRandomSampleSize() + "_" +
            "RT" + "_" + config.getRestartTemp() + "_" +
            "DD" + "_" + config.getDeltaDecay() + "_" +
            "A" + "_" + config.getAlpha() + "_" +
            "R" + "_" + config.getRounds() + ".txt";

    if (!resultFileCreated) {
      File outputDir = new File(config.getOutputDir());
      if (!outputDir.exists()) {
        if (!outputDir.mkdir()) {
          throw new IOException("Unable to create the output directory");
        }
      }
      // create folder and result file with header
      String header = "# Migration is number of nodes that have changed color.";
      header += "\n\nRound" + delimiter + "Edge-Cut" + delimiter + "Swaps" + delimiter + "Migrations" + delimiter + "Skipped" + "\n";
      FileIO.write(header, outputFilePath);
      resultFileCreated = true;
    }

    FileIO.append(round + delimiter + (edgeCuts) + delimiter + numberOfSwaps + delimiter + migrations + "\n", outputFilePath);
  }
}
