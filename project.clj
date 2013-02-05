(defproject tweetlocker "0.1.0-SNAPSHOT"
  :description "A personal Twitter archive."
  :dependencies [[org.clojure/clojure "1.4.0"]
                 [org.clojure/tools.logging "0.2.6"]
                 [fs "1.3.2"]
                 [cheshire "5.0.1"]
                 [oauth-clj "0.1.2"]
                 [compojure "1.1.5" :exclusions [ring/ring-core]]
                 [hiccup "1.0.2"]]
  :plugins [[lein-ring "0.8.2" :exclusions [org.clojure/clojure]]]
  :ring {:handler tweetlocker.web/app})
