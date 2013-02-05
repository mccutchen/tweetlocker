(ns tweetlocker.web
  (:use [clojure.pprint :only (pprint)]
        compojure.core
        [hiccup.middleware :only (wrap-base-url)]
        [hiccup core page])
  (:require [clojure.tools.logging :as log]
            [compojure.route :as route]
            [compojure.handler :as handler]))

(defn wrap-request-logging [app]
  (fn [{:keys [request-method uri] :as req}]
    (log/debug req)
    (let [start (System/currentTimeMillis)
          resp (app req)
          finish (System/currentTimeMillis)
          time (- finish start)
          status (:status resp)
          method (.toUpperCase (name request-method))]
      (log/info (format "%d %s %s %dms" status method uri time))
      resp)))

(defn render-page
  [title & body]
  (html5
    [:head
     [:title title]
     (include-css "/css/style.css")]
    [:body
     [:h1 title]
     body]))

(defn index-page
  [request]
  (render-page
   "Test Page"
   [:a {:href "/oauth"} "OAuth"]
   [:pre (with-out-str (pprint request))]))

(defroutes app-routes
  (GET "/" request (index-page request))
  (route/resources "/static")
  (route/not-found "Page not found"))

(def app
  (-> (handler/site app-routes)
      (wrap-base-url)
      (wrap-request-logging)))
