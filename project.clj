(defproject tweetlocker "0.1.0-SNAPSHOT"
  :description "A personal Twitter archive."
  :dependencies [[org.clojure/clojure "1.4.0"]
                 [fs "1.3.2"]
                 [cheshire "4.0.4"]
                 [oauth-clj "0.1.1-SNAPSHOT"]
                 [compojure "1.1.3"]
                 [hiccup "1.0.2"]]
  :plugins [[lein-ring "0.7.5"]]
  :ring {:handler tweetlocker.web/app})
