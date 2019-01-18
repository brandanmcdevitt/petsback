from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import random
import time
import os
import string

from flask import Flask, jsonify, request, render_template, redirect
from config import INPUT_HEIGHT, INPUT_WIDTH, INPUT_MEAN, INPUT_STD, INPUT_LAYER, OUTPUT_LAYER, MODEL_FILE, LABEL_FILE

import numpy as np
import tensorflow as tf

app = Flask(__name__)

def load_graph(model_file):
  graph = tf.Graph()
  graph_def = tf.GraphDef()

  with open(model_file, "rb") as f:
    graph_def.ParseFromString(f.read())
  with graph.as_default():
    tf.import_graph_def(graph_def)

  return graph

def read_tensor_from_image_file(file_name, input_height=299, input_width=299,
                                  input_mean=0, input_std=255):
  
  input_name = "file_reader"
  output_name = "normalized"
  file_reader = tf.read_file(file_name, input_name)
  if file_name.endswith(".png"):
    image_reader = tf.image.decode_png(file_reader, channels = 3,
                                       name='png_reader')
  elif file_name.endswith(".gif"):
    image_reader = tf.squeeze(tf.image.decode_gif(file_reader,
                                                  name='gif_reader'))
  elif file_name.endswith(".bmp"):
    image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
  else:
    image_reader = tf.image.decode_jpeg(file_reader, channels = 3,
                                        name='jpeg_reader')
  float_caster = tf.cast(image_reader, tf.float32)
  dims_expander = tf.expand_dims(float_caster, 0);
  resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
  normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
  sess = tf.Session()
  result = sess.run(normalized)

  return result

def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label


def classify(file_name, user_id, form):
  t = read_tensor_from_image_file(file_name,
                                  input_height=INPUT_HEIGHT,
                                  input_width=INPUT_WIDTH,
                                  input_mean=INPUT_MEAN,
                                  input_std=INPUT_STD)

  graph = load_graph(MODEL_FILE)                                
  with tf.Session(graph=graph) as sess:
    start = time.time()
    input_name = "import/" + INPUT_LAYER
    output_name = "import/" + OUTPUT_LAYER
    input_operation = graph.get_operation_by_name(input_name);
    output_operation = graph.get_operation_by_name(output_name);
    results = sess.run(output_operation.outputs[0],
                      {input_operation.outputs[0]: t})
    end=time.time()
    results = np.squeeze(results)

    top_k = results.argsort()[-5:][::-1]
    labels = load_labels(LABEL_FILE)

    #print('\nEvaluation time (1-image): {:.3f}s\n'.format(end-start))
    best_guess_name = ""
    best_guess_result = 0
    for i in top_k:
      if results[i] > best_guess_result:
        best_guess_name = labels[i]
        best_guess_result = results[i]
      #print(labels[i], results[i])

    best_guess_result = round(best_guess_result, 3) * 100
    best_guess_result = int(best_guess_result)
    best_guess_name = best_guess_name.split(' ', 1)
    best_guess_name = string.capwords(best_guess_name[1])
    breed = {}

    breed["breed"] = best_guess_name
    breed["result"] = best_guess_result
    return jsonify({"breed": breed})