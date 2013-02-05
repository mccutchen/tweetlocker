(ns tweetlocker.oauth
  (:require [tweetlocker.core :as locker]
            [oauth.twitter :as twitter]))

(def ^:dynamic *consumer-key* (System/getenv "CONSUMER_KEY"))
(def ^:dynamic *consumer-secret* (System/getenv "CONSUMER_SECRET"))

(defn make-oauth-client
  "Create a Twitter OAuth client for a user."
  [user-id]
  (let [access-token (locker/read-access-token user-id)]
    (twitter/oauth-client *consumer-key*
                          *consumer-secret*
                          (:token access-token)
                          (:secret access-token))))
