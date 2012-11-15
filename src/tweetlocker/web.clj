(ns tweetlocker.web
  (:use compojure.core
        [hiccup.middleware :only (wrap-base-url)]
        [hiccup core page])
  (:require [compojure.route :as route]
            [compojure.handler :as handler]))

(defn index-page []
  (html5
    [:head
      [:title "Tweetlocker!"]
      (include-css "/css/style.css")]
    [:body
      [:h1 "Tweetlocker!"]]))

(defroutes app-routes
  (GET "/" [] (index-page))
  (route/resources "/static")
  (route/not-found "Page not found"))

(def app
  (-> (handler/site app-routes)
      (wrap-base-url)))
