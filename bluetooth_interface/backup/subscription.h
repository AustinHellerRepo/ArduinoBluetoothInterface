
#include "unique_ptr.h"
#include "vector.h"


struct find_if_fn {
  template< std::input_iterator I, std::sentinel_for<I> S,
            class Proj = std::identity,
            std::indirect_unary_predicate<std::projected<I, Proj>> Pred >
  constexpr I operator()( I first, S last, Pred pred, Proj proj = {} ) const
  {
      for (; first != last; ++first) {
          if (std::invoke(pred, std::invoke(proj, *first))) {
              return first;
          }
      }
      return first;
  }
 
  template< ranges::input_range R, class Proj = std::identity,
            std::indirect_unary_predicate<std::projected<ranges::iterator_t<R>, Proj>> Pred >
  constexpr ranges::borrowed_iterator_t<R>
    operator()( R&& r, Pred pred, Proj proj = {} ) const
  {
    return (*this)(ranges::begin(r), ranges::end(r), std::ref(pred), std::ref(proj));
  }
};
 
inline constexpr find_if_fn find_if;

template<class ForwardIt, class UnaryPredicate>
ForwardIt remove_if(ForwardIt first, ForwardIt last, UnaryPredicate p)
{
    first = std::find_if(first, last, p);
    if (first != last)
        for(ForwardIt i = first; ++i != last; )
            if (!p(*i))
                *first++ = std::move(*i);
    return first;
}

template<class... Args>
class SubscriberBase {
public:
    virtual void call(Args... args) = 0;
    virtual bool instanceIs(void* t) = 0;
    virtual ~SubscriberBase() { };
};

template<class T, class... Args>
class Subscriber : public SubscriberBase<Args...> {
private:
    T* t;
    void(T::*f)(Args...);
public:
    Subscriber(T* _t, void(T::*_f)(Args...)) : t(_t), f(_f) { }
    void call(Args... args)   final { (t->*f)(args...); }
    bool instanceIs(void* _t) final { return _t == (void*)t; }
    ~Subscriber()             final { }
};

// our Listener will derive from EventListener<Listener>
// which holds a list of a events it is subscribed to.
// As these events will have different sigs, we need a base-class.
// We will store pointers to this base-class.
class EventBase { 
public:
    virtual void removeSubscriber(void* t) = 0;
};

template<class... Args>
class Event : public EventBase {
private:
    using SmartBasePointer = UniquePtr<SubscriberBase<Args...>>;
    Vector<SmartBasePointer> subscribers;
public:
    void fire(Args... args) {
        for (auto& f : subscribers)
            f->call(args...);
    }

    template<class T>
    void addSubscriber(T* t, void(T::*f)(Args... args)) {
        auto s = new Subscriber <T, Args...>(t, f);
        subscribers.push_back(SmartBasePointer(s));
    }

    //template<class T>
    void removeSubscriber(void* t) final {
        auto to_remove = std::remove_if(
            subscribers.begin(),
            subscribers.end(),
            [t](auto& s) { return s->instanceIs(t); }
        );
        subscribers.erase(to_remove, subscribers.end());
    }
};

// derive your listener classes: struct MyListener : EventListener<MyListener>, i.e. CRTP
template<class Derived>
class EventListener {
private:
    // all events holding a subscription to us...
    Vector<EventBase*> events;

public:
    template<class... Args>
    void connect(Event<Args...>& ev, void(Derived::*listenerMethod)(Args... args)) {
        ev.addSubscriber((Derived*)this, listenerMethod);
        events.push_back(&ev);
    }

    // ...when the listener dies, we must notify them all to remove subscription
    ~EventListener() {
        for (auto& e : events)
            e->removeSubscriber((void*)this);
    }
};
