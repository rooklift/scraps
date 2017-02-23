func GetSubPlan(g *gohalite.Game, plan *Plan) []int {

    var result []int

    for n := 0 ; n < plan.depth ; n++ {

        index := plan.order[n]

        if g.Owner[index] != g.Id {
            result = append(result, index)
        }
    }

    return result
}

// -------------------------------------------------------------------------------------------------------------

type Plan struct {
    order       [MAX_PLAN_DEPTH]int // The order of expansion
    turns       int                 // How many turns this plan takes (maybe approximate)
    production  int                 // How much production this plan ends with
    depth       int
}

func Precompute(g *gohalite.Game) *Plan {

    var plan *Plan = new(Plan)

    var start_index int
    for i := 0 ; i < g.Size ; i++ {     // Find start spot
        if g.Owner[i] == g.Id {
            start_index = i
            break
        }
    }

    AddToPlan(g, plan, start_index)

    log.Dump("Precompute took %v (depth == %d)", time.Since(g.GameStart), MAX_PLAN_DEPTH)
    log.Dump("%v", plan.order)

    return plan
}

func AddToPlan(g * gohalite.Game, plan *Plan, index int) {

    // We send information back to the caller by modifying *plan

    plan.order[plan.depth] = index
    if plan.depth > 0 {
        plan.turns += g.Strength[index] / (plan.production) + 1     // Very rough approximation of how long it takes to capture this
    } else {
        plan.turns = 0
    }
    plan.production += g.Production[index]
    plan.depth += 1

    if plan.depth == MAX_PLAN_DEPTH {
        return
    }

    choices := make([]*Plan, 0, 4)

    for n := 0 ; n < plan.depth ; n++ {

        source_i := plan.order[n]

        for _, neighbour := range g.Neighbours[source_i] {

            neigh_i := neighbour.Index

            already_captured_neighbour := false
            for z := 0 ; z < plan.depth ; z++ {
                if plan.order[z] == neigh_i {
                    already_captured_neighbour = true
                    break
                }
            }

            if already_captured_neighbour == false && g.Owner[neigh_i] == 0 {
                plan_copy := new(Plan)
                *plan_copy = *plan
                AddToPlan(g, plan_copy, neigh_i)
                choices = append(choices, plan_copy)
            }
        }
    }

    if len(choices) == 0 {
        return
    }

    if len(choices) == 1 {
        *plan = *choices[0]
        return
    }

    best := float32(0)
    var best_choice *Plan

    for _, choice := range choices {
        score := float32(choice.production) / float32(choice.turns)
        if score > best {
            best = score
            best_choice = choice
        }
    }

    if best_choice != nil {
        *plan = *best_choice
    }
}
