(ns user (:require [cheshire.core :as json]))
(ns user (:require [clojure.java.io :as io]))
(ns user (:require [instaparse.core :as insta]))

(def musicians (json/decode-stream (io/reader "../../jazzdisco/musicians.json")))
(doseq [{first-name "first_name" last-name "last_name" slug "slug"} musicians] (println first-name last-name slug))


(def objects (json/decode-stream (io/reader "../../jazzdisco/items.json")))

(def parse-personnel (insta/parser
  "S = (names (<openparen> instruments <closeparen>)?)+ <whitespace>? (<replaces> <whitespace> replacee)? <samesession>? <samepersonnel>?
   names = name (<comma> name)*
   name = word (<whitespace> word)*
   instruments = instrument (<comma> instrument)*
   instrument = word (<whitespace> word)* (<whitespace> tracks)?
   replacee = word (<whitespace> word)*
   replaces = #'replaces'
   <samesession> = #': same session'
   <samepersonnel> = #': same personnel'
   tracks = #'-\\d+([,/]\\d+)*'
   <word> = #'[a-zA-Z\\.\"\\'\\-]+'
   whitespace = #'\\s+'
   openparen = #'\\s*\\('
   closeparen = #'\\)\\s*'
   comma = #',\\s*'"))

(ns user (:require [cheshire.core :as json]))
(ns user (:require [clojure.java.io :as io]))
(ns user (:require [instaparse.core :as insta]))

(def objects (json/decode-stream (io/reader "../../jazzdisco/items.json")))

(filter #(= (% "type") "Person") objects)

(def recordings (filter #(= (% "type") "Recording") objects))
(count recordings)

(defn extract-personnel-from-recording [recording] (map #(% "personnel") (recording "parts")))
(defn extract-personnel-from-recordings [recordings] (mapcat extract-personnel-from-recording recordings))
(defn extract-personnel [recordings] (map parse-personnel (extract-personnel-from-recordings recordings)))

(extract-personnel (take 5 recordings))

;(extract-personnel recordings)
