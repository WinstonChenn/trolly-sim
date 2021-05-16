import os, random
import matplotlib.pyplot as plt
import numpy as np
from agents_utils import RandomAgent, AlwaysDoNothingAgent, AlwaysSwitchAgent,\
                         TrackLifeAgent, StatAgent
from sim_utils import Simulator, LossType


def homo_exp(n):
    full_info_losses = {"tele": [], "deon": []}
    part_info_losses = {"tele": [], "deon": []}
    loss_dicts = [part_info_losses, full_info_losses]
    agent_cons_arr = [RandomAgent, AlwaysDoNothingAgent,
                      AlwaysSwitchAgent, TrackLifeAgent, StatAgent]
    agent_label_arr = [str(Cons(0)) for Cons in agent_cons_arr]

    for full_info in [0, 1]:
        print(f"start homogenous experiments, full_info={full_info}, n={n}")
        simulator = Simulator(n=n, full_info=full_info, seed=0)

        for Cons in agent_cons_arr:
            agent_arr = [Cons(0) for i in range(n)]
            simulator.batch_set_trollies(agent_arr)
            for i in range(1000):
                simulator.refresh_track_nums()
                simulator.refresh_pass_nums()
                simulator.run_trial()

            tele_loss = simulator.get_tot_tele_loss()
            deon_loss = simulator.get_tot_deon_loss()
            print(f"{agent_arr[0]}: tele_loss={tele_loss:.3f},"
                  f"deon_loss={deon_loss:.3f}")
            loss_dicts[full_info]['tele'].append(tele_loss)
            loss_dicts[full_info]['deon'].append(deon_loss)
            simulator.clear_records()
        print()

    plot_dir = "../plots"
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    plot_url = os.path.join(plot_dir, f"homo_exp_loss_plot_n={n}.png")
    title = f"homogenous experiment loss plot n={n}"
    plot_losses(plot_url, title, loss_dicts, agent_label_arr)


def mix_exp(n):
    full_info_losses = {"tele": [], "deon": []}
    part_info_losses = {"tele": [], "deon": []}
    loss_dicts = [part_info_losses, full_info_losses]

    agent_cons_arr = [RandomAgent, AlwaysDoNothingAgent,
                      AlwaysSwitchAgent, TrackLifeAgent, StatAgent]
    agent_label_arr = [str(Cons(0)) for Cons in agent_cons_arr]
    if n % len(agent_label_arr) != 0:
        raise ValueError(f"n={n} not a divisible by number of"
                         f"agent types={len(agent_label_arr)}")
    agent_arr = []
    for i in range(n//len(agent_cons_arr)):
        for Cons in agent_cons_arr:
            agent_arr.append(Cons(0))
    random.shuffle(agent_arr)
    agent_str_arr = [str(agent) for agent in agent_arr]
    assert len(agent_arr) == len(agent_str_arr) == n

    for full_info in [0, 1]:
        print(f"start mixed experiments, full_info={full_info} n={n}")
        simulator = Simulator(n=n, full_info=full_info, seed=0)
        simulator.batch_set_trollies(agent_arr)
        for i in range(1000):
            simulator.refresh_track_nums()
            simulator.refresh_pass_nums()
            simulator.run_trial()

        for label in agent_label_arr:
            indices = [i for i, x in enumerate(agent_str_arr) if x == label]
            tele_loss = simulator.get_tele_loss_by_idx(indices)
            deon_loss = simulator.get_deon_loss_by_idx(indices)
            print(f"{label}: tele_loss={tele_loss:.3f}, deon_loss={deon_loss:.3f}")
            loss_dicts[full_info]['tele'].append(tele_loss)
            loss_dicts[full_info]['deon'].append(deon_loss)
        print()

    plot_dir = "../plots"
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    plot_url = os.path.join(plot_dir, f"mix_exp_loss_plot_n={n}.png")
    title = f"mixed experiment loss plot n={n}"
    plot_losses(plot_url, title, loss_dicts, agent_label_arr)


def mix_comp_exp(n, num_round=10, num_sim=100, ratio=0.1):
    """
    n: number of trollies in the experiment
    num_round: number of rounds to compete
    num_sim: number of simulations in each round
    ratio: top/bottom percentage to repopulate and eliminate
    """
    agent_cons_arr = [RandomAgent, AlwaysDoNothingAgent,
                      AlwaysSwitchAgent, TrackLifeAgent, StatAgent]
    agent_label_arr = [str(Cons(0)) for Cons in agent_cons_arr]
    if n % len(agent_label_arr) != 0:
        raise ValueError(f"n={n} not a divisible by number of"
                         f"agent types={len(agent_label_arr)}")

    # data structure that stores agent counts by type in each round
    agent_type_count_dict = {
        LossType.TELE.value: [{label: 0 for label in agent_label_arr}
                                for i in range(num_round+1)],
        LossType.DEON.value: [{label: 0 for label in agent_label_arr}
                                for i in range(num_round+1)]}

    for loss_type in [LossType.TELE, LossType.DEON]:
        agent_type_count = agent_type_count_dict[loss_type.value]
        # initialize agents (all balanced amount)
        agent_arr = []
        for _ in range(n//len(agent_cons_arr)):
            for Cons in agent_cons_arr:
                agent_arr.append(Cons(0))
                # increment agent count
                agent_type_count[0][str(agent_arr[-1])] += 1
        random.shuffle(agent_arr)

        full_info = 1  # fixed full_info
        simulator = Simulator(n=n, full_info=full_info, seed=0)
        simulator.batch_set_trollies(agent_arr)
        for i_round in range(1, num_round+1):
            print(f"start round {i_round} loss type={loss_type.value}")
            # perform 100 simulations
            for i_sim in range(100):
                simulator.refresh_track_nums()
                simulator.refresh_pass_nums()
                simulator.run_trial()
            
            # eliminate and repopulate max(1, top/bot 10%)
            rep_idx_arr, eli_idx_arr = \
                simulator.get_top_bot_n_trolly_idx(n=max(1, int(ratio*n)),
                                                   loss_type=loss_type)

            assert len(rep_idx_arr) == len(eli_idx_arr)
            for i_rep in range(len(rep_idx_arr)):
                rep_idx = rep_idx_arr[i_rep]
                eli_idx = eli_idx_arr[i_rep]
                label_idx = agent_label_arr.index(
                    simulator.get_trolly_str_by_idx(rep_idx))
                RepCons = agent_cons_arr[label_idx]
                simulator.set_trolly_by_idx(eli_idx, RepCons(0))
            simulator.shuffle_trolly_arr()
            agent_str_arr = simulator.get_trolly_str_arr()
            for label in agent_label_arr:
                agent_type_count[i_round][label] += agent_str_arr.count(label)
                print(f"number of {label} = {agent_str_arr.count(label)}",
                      end="\t")
            print()

    plot_url = os.path.join("..", "plots", f"mix_comp_agent_count_plot_n={n}_"
                            f"#rounds={num_round}_"f"#sim={num_sim}_"
                            f"ratio={ratio}.png")
    title=f"n={n} #rounds={num_round} #simulations={num_sim} ratio={ratio}"
    plot_agent_count(plot_url, title, agent_type_count_dict, agent_label_arr)
        


def plot_losses(plot_url, title, loss_dicts, agent_label_arr):
    
    full_loss = loss_dicts[0]
    part_loss = loss_dicts[1]

    if "tele" not in full_loss or "deon" not in full_loss or \
            "tele" not in part_loss or "deon" not in part_loss:
        raise ValueError("loss dict doesn't contain required keys:"
                         "tele\", \"deon\"")

    fig, axes = plt.subplots(1, 2, figsize=[15, 6])
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.suptitle(title, fontsize=20)

    axes[0].plot(agent_label_arr, part_loss["tele"],
                 label="partical information", marker="o")
    axes[0].plot(agent_label_arr, full_loss["tele"],
                 label="full information", marker="o")
    axes[0].set_title("teleology loss")
    axes[0].legend()

    axes[1].plot(agent_label_arr, part_loss["deon"],
                 label="partial information", marker="o")
    axes[1].plot(agent_label_arr, full_loss["deon"],
                 label="full information", marker="o")
    axes[1].set_title("deontology loss")
    axes[1].legend()

    print(f"save loss plot at={plot_url}")
    fig.savefig(plot_url)


def plot_agent_count(plot_url, title, count_dict, agent_label_arr):
    if LossType.TELE.value not in count_dict \
        or LossType.DEON.value not in count_dict:
        raise ValueError("count dict doesn't contain required keys:"
                         "\"teleology\", \"deontology\"")

    fig, axes = plt.subplots(2, 1, figsize=[18, 10])
    fig.tight_layout(rect=(0.01, 0.01, 1, 0.95))
    plt.subplots_adjust(hspace=0.2)
    fig.suptitle(title, fontsize=20)
    for loss_i, loss_type in enumerate([LossType.TELE, LossType.DEON]):
        data = [[round_dict[label] for round_dict in
                 count_dict[loss_type.value]] for label in agent_label_arr]
        X = np.arange(len(count_dict[loss_type.value]))*2-0.5
        axes[loss_i].set_title(loss_type.value+" loss")
        axes[loss_i].set_xticks(np.arange(len(count_dict[loss_type.value]))*2)
        axes[loss_i].set_xticklabels(np.arange(len(count_dict[loss_type.value])))
        axes[loss_i].set_xlabel("competition rounds")
        axes[loss_i].set_ylabel("trolly agent count")
        for label_i, label in enumerate(agent_label_arr):
            axes[loss_i].bar(X + 0.25*label_i, data[label_i], width=0.25,
                             label=label if loss_i == 0 else "")
    fig.legend()
    fig.savefig(plot_url)


def main():
    simulator = Simulator(n=5, full_info=0, seed=0)

    randAg = RandomAgent(0)
    adnAg = AlwaysDoNothingAgent(0)
    asAg = AlwaysSwitchAgent(0)
    tlAg = TrackLifeAgent(0)
    statAg = StatAgent(0)
    agent_arr = [randAg, adnAg, asAg, tlAg, statAg]
    simulator.batch_set_trollies(agent_arr)
    for i in range(20):
        simulator.refresh_track_nums()
        simulator.refresh_pass_nums()
        simulator.run_trial()
        print(simulator.get_tot_tele_loss())
        print(simulator.get_tot_deon_loss())



if __name__ == "__main__":
    main()
    for n in [2, 5, 15, 20, 50, 100]:
        homo_exp(n)
    for n in [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]:
        mix_exp(n)
    for n in [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]:
        mix_comp_exp(n=n, num_round=10, num_sim=100, ratio=0.2)
